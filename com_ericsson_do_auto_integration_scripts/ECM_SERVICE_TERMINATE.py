from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *


log = Logger.get_logger('ECM_SERVICE_TERMINATE.py')





def get_ns_instance_id(connection,token,core_vm_hostname):
    try:
        log.info("Start to fecth Network Service Id")
        Report_file.add_line('Start to Fetch Network Service Id ')
        count = 0
        vapp_list = get_vapp_list_from_eocm(connection,token,core_vm_hostname,"ALL")
        for vapp_dict in vapp_list:
            if 'networkServices' in vapp_dict:
                networkservcies = vapp_dict['networkServices']
                for line in networkservcies:
                    name = line['name']
                    if name == 'nsd-cnf':
                        id = line['id']
                        log.info('Fetching ns_instance_id from vapp_list '+name+' , id - '+id)
                        Report_file.add_line('Fetching ns_instance_id from vapp_list ' + name + ' , id - ' + id)
                        count = count + 1
                        return id
                    
        if count == 0: 
                log.info("There is no networkservices in the vapp list")
                Report_file.add_line("There is no networkservices in the vapp list")
                return "NO_NETSERV"
      
        
    except Exception as e:

        log.error('Error Fetching Network Service Id ' + str(e))
        Report_file.add_line('Error Fetching Network Service Id ' + str(e))
        assert False
        
def terminate_ns_instantiate():
    try:
        
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities,connection,core_vm_hostname)
        ns_instances_id = get_ns_instance_id(connection,token,core_vm_hostname)
        
        if  ns_instances_id == 'NO_NETSERV': 
        
            log.info('Since there is no Networkservices in the vapp list, Job will not do the termination of ns')
            Report_file.add_line('Since there is no Networkservices in the vapp list, Job will not do the termination of ns')
        
        else:
            terminate_ns(connection,ns_instances_id)
       
                    
    except Exception as e:

        log.error('Error while terminate Instantiate NS ' + str(e))
        Report_file.add_line('Error while terminate Instantiate NS ' + str(e))
        assert False
    finally:
        connection.close()
    

def delete_instantiate_ns(connection,ns_instances_id):
    try:
        log.info('Terminating of NS Instantiate has been failed, Hence deleting the NS ')
        Report_file.add_line('Terminating of NS Instantiate has been failed, Hence deleting the NS')
        
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        token = Common_utilities.authToken(Common_utilities,connection,core_vm_ip)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        command = '''curl --insecure "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}"  -X "DELETE"   -H "AuthToken: {}"'''.format(core_vm_hostname,ns_instances_id,token)
        
        Report_file.add_line('Command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('deleting NS Instantiate command output : ' + command_output)

        if '204 No Content' in command_output:
        
            log.info('NS Instantiate Deleted Successfully')
            
            Report_file.add_line('NS Instantiate Deleted Successfully')
        
        else:
            
            log.error('NS Instantiate Deletion failed ')
            Report_file.add_line('NS Instantiate Deletion failed ')
            assert False
            
    except Exception as e:

        log.error('Error while deleting NS Instantiate  ' + str(e))
        Report_file.add_line('Error while deleting NS Instantiate ' + str(e))
        assert False
          
def terminate_ns(connection,ns_instances_id):
    try:
        log.info('Start to terminate Instantiate NS' )
        Report_file.add_line('Start to terminate Instantiate NS')
        
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        token = Common_utilities.authToken(Common_utilities,connection,core_vm_hostname)
        
        file_name = "terminate_NS.json"
        
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name, file_name)
        time.sleep(2)
        
        command = '''curl --insecure -i -X POST "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}/terminate" -H "AuthToken: {}" -H "Content-Type: application/json"  --data @{}'''.format(core_vm_hostname,ns_instances_id,token,file_name)
        
        Report_file.add_line('Command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        output = command_output
        Report_file.add_line('terminating Instantiate NS command output : ' + command_output)

        if '202 Accepted' in output:
            orderid = output.split('\\r\\n')[2]
            order_id  = orderid.split(': ')[1]
            log.info('Instantiate NS Order Id - '+order_id)
            Report_file.add_line('Instantiate NS Order Id -' + order_id)
           
            token = Common_utilities.authToken(Common_utilities,connection,core_vm_hostname)
            
            order_status, order_output = Common_utilities.NSorderReqStatus(Common_utilities, connection, token, core_vm_hostname,order_id, 10)
            if order_status:
                log.info("Successfully Terminated Instantiation of NS")
               
                Report_file.add_line('Successfully Terminated Instantiation of NS')

            else:
                log.file("Failed to terminate NS. Hence deleting the NS")
                Report_file.add_line('Failed to terminate NS. Hence deleting the NS')
                delete_instantiate_ns(connection,ns_instances_id)
               
                
        else:
            log.info('Error While deleting Instantiation of NS')
            Report_file.add_line('Error While deleting Instantiation of NS')
            assert False        
        
        
        
    except Exception as e:

        log.error('Error while terminate Instantiate NS ' + str(e))
        Report_file.add_line('Error while terminate Instantiate NS ' + str(e))
        assert False
   