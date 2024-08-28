# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************
'''
Created on 16 April 2020


@author: eiaavij
'''

import ast
import time
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.LPIS_files_update import (
    update_register_vm_vnfm, update_nfvo_vm_vnfm, update_vim_vm_vnfm
)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (
    update_lcm_oss_password, vm_vnfm_lcm_workflow_installation_validation
)
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (
    get_VMVNFM_host_connection, get_testhotel_vmvnfm_host_connection, transfer_director_file_to_vm_vnfm,
    run_command_vm_vnfm_db
)

log = Logger.get_logger('VM_VNFM_LCM_ECM_INTEGRATION.py')


def register_vm_vnfm(app=False):
    try:

        log.info('Start to register VM VNFM LCM')
        Report_file.add_line('Start to register VM VNFM LCM ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        file_name = 'vm_vnfm_register.json'

        vm_vnfm_manager_name = Common_utilities.get_name_with_timestamp(Common_utilities, vm_vnfm_namespace)
        if app == 'TEST-HOTEL':
            update_register_vm_vnfm(file_name, vm_vnfm_manager_name, "TEST-HOTEL-VM-VNFM-INTE")
            nested_conn = get_testhotel_vmvnfm_host_connection(directory_server_ip, directory_server_username)

        else:
            update_register_vm_vnfm(file_name, vm_vnfm_manager_name)
            nested_conn = get_VMVNFM_host_connection()

        log.info('Transferring vm_vnfm_register.json file to director server ip %s', directory_server_ip)

        ServerConnection.put_file_sftp(nested_conn,
                                        r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file_name,
                                        r'/home/' + directory_server_username + '/' + file_name)

        time.sleep(2)

        #source = '/home/' + directory_server_username + '/' + file_name
        #destination = '/' + file_name
        source = f'/home/{directory_server_username}/{file_name}'
        destination = f'/tmp/{file_name}'

        log.info('Transferring vm_vnfm_register.json file to eric-vnflcm-service-0 pod ')

        transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

        time.sleep(2)

        log.info('Generating token to register VM VNFM')

        token = Common_utilities.podauthToken(Common_utilities, nested_conn, core_vm_ip)

        log.info('Register VM VNFM with curl command  ')
        cmd = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c '.format(
            vm_vnfm_namespace)
        curl = cmd + '''{}curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/vnfms{}{}'''.format(
            '"', token, destination, core_vm_hostname, "'", '"')
        command = curl
        log.info('Command to execute %s', command)
        Report_file.add_line('register command : ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())

        Report_file.add_line('register command output : ' + command_output)
        log.info('Command output: %s', command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            subscription_string = ast.literal_eval(command_output[2:-1:1])
            if 'data' in subscription_string.keys():
                global subscription_id
                subscription_id = subscription_string['data']['vnfm']['id']
                log.info('vm vnfm subscription id %s', subscription_id)
                Report_file.add_line('VM VNFM Subscription id : ' + subscription_id)

                log.info('updating run time file with VN VNFM manager name and subscription id ')
                update_runtime_env_file('VM_VNFM_MANAGER_ID', subscription_id)
                time.sleep(2)
                update_runtime_env_file('VM_VNMF_MANAGER_NAME', vm_vnfm_manager_name)

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for registering the VM VNFM %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for registering the VM VNFM')
            assert False
    except Exception as e:
        log.error('Error registering VM VNFM LCM %s', str(e))
        Report_file.add_line('Error registering VM VNFM LCM' + str(e))
        assert False
    finally:
        nested_conn.close()


def add_nfvo_vm_vnfm(app=False):
    try:

        log.info('Start to add NFVO VM VNFM LCM')
        Report_file.add_line('Start to add NFVO VM VNFM LCM ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        file_name = 'vm_vnfm_nfvo.json'
        update_nfvo_vm_vnfm(file_name, subscription_id)

        time.sleep(2)
        if app == 'TEST-HOTEL':
            nested_conn = get_testhotel_vmvnfm_host_connection(directory_server_ip, directory_server_username)
        else:
            nested_conn = get_VMVNFM_host_connection()
        log.info('Transferring vm_vnfm_nfvo.json file to director server ip %s', directory_server_ip)
        ServerConnection.put_file_sftp(nested_conn,
                                        r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file_name,
                                        r'/home/' + directory_server_username + '/' + file_name)

        time.sleep(2)

        source = f'/home/{directory_server_username}/{file_name}'
        destination = f'/tmp/{file_name}'

        time.sleep(2)

        log.info('Transferring vm_vnfm_nfvo.json file to eric-vnflcm-service-0 pod ')
        transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

        # nested_conn = get_VMVNFM_host_connection()

        command = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c "sudo -E vnflcm nfvo add --file {}"'.format(
            vm_vnfm_namespace, destination)

        log.info('NFVO addition command %s', command)

        stdin, stdout, stderr = nested_conn.exec_command(command)

        command_output = str(stdout.read())

        log.info('Command output: %s', command_output)
        Report_file.add_line('Command Output : ' + command_output)

        if 'NFVO addition successful' in command_output:

            log.info('NFVO addition is successful ...')

        else:

            log.error('Something wrong in NFVO addition , please check command output for details %s', command_output)
            assert False

        log.info('Finished executing the command to add vm_vnfm_nfvo.json file ')
        Report_file.add_line('Finished executing the command to add vm_vnfm_nfvo.json file ')

    except Exception as e:
        log.error('Error registering VM VNFM LCM %s', str(e))
        Report_file.add_line('Error registering VM VNFM LCM ' + str(e))
        assert False
    finally:
        nested_conn.close()


def execute_vm_vnfm_vim_addition(nested_conn, command):
    stdin, stdout, stderr = nested_conn.exec_command(command)
    data = stdout.read().decode("utf-8")

    log.info('vim addition command executed : ' + command)
    Report_file.add_line('vim addition command executed ' + data)


def add_vim_vm_vnfm():
    try:

        log.info('Start to add VIM VM VNFM LCM')
        Report_file.add_line('Start to add VIM VM VNFM LCM ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        file_name = 'vm_vnfm_vim_addition.json'

        update_vim_vm_vnfm(file_name)

        nested_conn = get_VMVNFM_host_connection()

        log.info('transferring vm_vnfm_vim_addition.json to director server ip %s', directory_server_ip)
        ServerConnection.put_file_sftp(nested_conn,
                                        r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file_name,
                                        r'/home/' + directory_server_username + '/' + file_name)

        time.sleep(2)

        source = '/home/' + directory_server_username + '/' + file_name
        destination = f'/tmp/{file_name}'

        log.info('Transferring vm_vnfm_vim_addition.json file to eric-vnflcm-service-0 pod ')
        transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

        time.sleep(2)

        db_command = 'TRUNCATE vims cascade;'
        db_name = 'vnflafdb'

        db_output = run_command_vm_vnfm_db(nested_conn, db_command, db_name)

        Report_file.add_line('db command output ' + db_output)

        time.sleep(5)

        command = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c "sudo -E vnflcm vim add --file={}"'.format(
            vm_vnfm_namespace, destination)

        log.info('Executing vim vm vnfm addition command ')
        Report_file.add_line('Executing vim vm vnfm addition command : ' + command)

        execute_vm_vnfm_vim_addition(nested_conn, command)

        log.info('Finished adding VIM VM VNFM LCM ')
        Report_file.add_line('Finished adding VIM VM VNFM LCM ')


    except Exception as e:
        log.error('Error adding VIM VM VNFM LCM %s', str(e))
        Report_file.add_line('Error adding VIM VM VNFM LCM  ' + str(e))
        assert False
    finally:
        nested_conn.close()


def vm_vnfm_workflow_deployment():
    try:

        log.info('Start to deploy vm vnfm lcm  workflow bundle rpm ')
        Report_file.add_line('Start to deploy vm vnfm lcm  workflow bundle rpm')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        rpm_link = ecm_host_data._Ecm_core__rpm_bundle_link
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        nested_conn = get_VMVNFM_host_connection()

        log.info('Downloading RPM bundle file using the link provided in the DIT: %s', rpm_link)
        Report_file.add_line('Downloading rpm bundle file using the link provided in DIT')

        command = 'wget {}'.format(rpm_link)
        log.info('rpm wget command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)

        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        command = 'find ERICvnflaf*.rpm | xargs ls -rt | tail -1'
        log.info('find rpm command %s', command)

        stdin, stdout, stderr = nested_conn.exec_command(command)

        command_output = str(stdout.read())[2:-3:]
        log.info(command_output)

        rpmname = command_output
        log.info('rpm name : %s', rpmname)
        log.info('Workflow rpm file down loaded is: %s', command_output)
        Report_file.add_line('Workflow rpm  bundle file down loaded successfully.')

        log.info('Transferring workflow rpm to eric-vnflcm-service-0 pod %s', rpmname)

        source = '/home/' + directory_server_username + '/' + rpmname
        destination = f'/tmp/{rpmname}'

        transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

        time.sleep(20)

        command = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c "sudo -E wfmgr bundle install --package={}"'.format(
            vm_vnfm_namespace, destination)

        vm_vnfm_lcm_workflow_installation_validation(nested_conn, command, 'DUMMY')
        Common_utilities.clean_up_rpm_packages(Common_utilities, nested_conn, rpmname)

    except Exception as e:

        log.error('Error workflow bundle install on VM VNFM LCM')
        Report_file.add_line('Error workflow bundle install on VM VNFM LCM')
        assert False

    finally:
        nested_conn.close()


def vm_vnfm_oss_password_update():
    update_lcm_oss_password()


def enm_configuration_vm_vnfm():
    try:
        log.info('Start to configure enm on vm vnfm lcm ')
        Report_file.add_line('Start to configure enm on vm vnfm lcm')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        oss_master_hostname = sit_data._SIT__ossMasterHostName
        oss_master_host_ip = sit_data._SIT__ossMasterHostIP
        oss_user_name = sit_data._SIT__oss_user_name
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        nested_conn = get_VMVNFM_host_connection()

        kube_cmd = 'kubectl exec -it eric-vnflcm-service-0 -c eric-vnflcm-service -n {} -- bash -c '.format(
            vm_vnfm_namespace)

        ossHostName = kube_cmd + '{}/ericsson/pib-scripts/etc/config.py update --app_server_address localhost:8080 --name=ossHostName  --value={}{}'.format(
            '"', oss_master_hostname, '"')
        command = ossHostName
        Report_file.add_line('ossHostName command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('ossHostName command output ' + command_output)

        ossUserName = kube_cmd + '{}/ericsson/pib-scripts/etc/config.py update --app_server_address localhost:8080 --name=ossUserName  --value={}{}'.format(
            '"', oss_user_name, '"')
        command = ossUserName
        Report_file.add_line('ossUserName command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('ossUserName command output ' + command_output)

        ossSshPortNumber = kube_cmd + '{}/ericsson/pib-scripts/etc/config.py update --app_server_address localhost:8080 --name=ossSshPortNumber  --value={}{}'.format(
            '"', '22', '"')
        command = ossSshPortNumber
        Report_file.add_line('ossSshPortNumber command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('ossSshPortNumber command output ' + command_output)

        ossFtpPortNumber = kube_cmd + '{}/ericsson/pib-scripts/etc/config.py update --app_server_address localhost:8080 --name=ossFtpPortNumber  --value={}{}'.format(
            '"', '22', '"')
        command = ossFtpPortNumber
        Report_file.add_line('ossFtpPortNumber command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('ossFtpPortNumber command output ' + command_output)

        log.info('updating /etc/hosts file with Host Name and master host ip')

        command = kube_cmd + '{}grep -qxF {}{} {}{} /etc/hosts || echo -e {} {} | tee -a /etc/hosts{}'.format('"', "'",
                                                                                                              oss_master_host_ip,
                                                                                                              oss_master_hostname,
                                                                                                              "'",
                                                                                                              oss_master_host_ip,
                                                                                                              oss_master_hostname,
                                                                                                              '"')

        Report_file.add_line('/etc/hosts file update command ' + command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        # NOT reading the command output in Report or log file , because if nothing is updated in the file then there is NO OUTPUT

        log.info('End configuring enm on vm vnfm lcm ')
        Report_file.add_line('End configuring enm on vm vnfm lcm')

    except Exception as e:

        log.error('Error in configuration of enm on vm vnfm lcm %s', str(e))
        Report_file.add_line('Error in configuration of enm on vm vnfm lcm ' + str(e))
        assert False
    finally:
        nested_conn.close()
