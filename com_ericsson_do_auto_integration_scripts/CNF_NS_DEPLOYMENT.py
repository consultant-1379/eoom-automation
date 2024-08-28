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
Created on jul 17, 2020

@author: zsyapra
'''

import time
import json
import paramiko
import threading
from tabulate import tabulate

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_cnf_create_package_file,
                                                                         update_cnf_instanatiate_file,
                                                                         update_ns_create_package_file)
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler

import json
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import (delete_node_vnf_package,
                                                                           delete_cnf_nsd_packages,
                                                                           get_ecm_package_list)
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import (get_PSQL_connection,
                                                                 get_table_data_from_PSQL_table_for_ecm_package_deletion)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (fetch_nsd_details,
                                                                          upload_nsd_package,
                                                                          create_nsd_package)
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import delete_cnf_nsd_packages
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import get_package_upload_status
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('CNF_NS_DEPLOYMENT.py')
lock = threading.RLock()
report_table_data = []


def print_cnf_package_report():
    try:
        lock.acquire()
        log.info('Package report for all cnf packages ')
        Report_file.add_line('Package report for all cnf packages')
        log.info(tabulate(report_table_data, headers=["PACKAGE NAME", "UPLOAD STATUS"], tablefmt='grid',
                          showindex="always"))
        Report_file.add_line(
            tabulate(report_table_data, headers=["PACKAGE NAME", "UPLOAD STATUS"], tablefmt='grid',
                     showindex="always"))

        for data in report_table_data:
            if 'UPLOAD FAILED' in data:
                log.error('Failure in package upload , please check the above table for more details')
                Report_file.add_line(
                    'Failure in package upload of minimum one node , please check the above table for more details')
                assert False
    except Exception as e:
        log.error('Error package upload' + str(e))
        Report_file.add_line('Error package upload' + str(e))
        assert False
    finally:
        lock.release()


def add_report_data_in_cnf_package_report(package_name, package_status):
    try:
        for data in report_table_data:
            if package_name in data:
                return

        report_data = [package_name, package_status]
        report_table_data.append(report_data)

    except Exception as e:
        log.info('Error adding report data in report table :' + e)


def upload_cnf_package(connection, token, vnf_instance_id, core_vm_hostname, cnf_package_name, pkg_dir_path,
                       idlist):
    try:
        log.info('Start to upload CNF package' + str(cnf_package_name))
        Report_file.add_line('Start to upload CNF package' + str(cnf_package_name))
        cd_cmd = 'cd ' + pkg_dir_path
        curl_command = '''curl --insecure -i --location --request PUT "https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages/{}/package_content" --header 'Content-Type: application/zip' --header 'AuthToken:{}' -T "{}"'''.format(
            core_vm_hostname, vnf_instance_id, token, cnf_package_name)
        command = cd_cmd + ';' + curl_command
        Report_file.add_line('Command : ' + command)
        log.info(" Package " + str(cnf_package_name) + " Upload in progress, please wait....")

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('command output : ' + command_output)
        output = command_output
        global report_table_data
        if '100 Continue' in output:
            time_out = 3600
            wait_time = 90
            status = get_package_upload_status(connection, token, core_vm_hostname, vnf_instance_id, time_out,
                                               wait_time)

            if status == 'UPLOADED':
                log.info('Package ' + str(cnf_package_name) + ' uploaded successfully. ')
                Report_file.add_line('Package ' + str(cnf_package_name) + ' uploaded successfully. ')
                add_report_data_in_cnf_package_report(cnf_package_name, 'UPLOADED')
            else:
                log.info('Package ' + str(cnf_package_name) + ' upload failed. ')
                Report_file.add_line('Package ' + str(cnf_package_name) + ' upload failed. ')
                add_report_data_in_cnf_package_report(cnf_package_name, 'UPLOAD FAILED')
        else:
            Report_file.add_line('Error in Upload CNF package')
            assert False
    except Exception as e:
        log.error('Error while Uploading CNF package ' + cnf_package_name + ' ' + str(e))
        Report_file.add_line('Error while uploading CNf package ' + cnf_package_name + ' ' + str(e))

        for i in idlist:
            log.info("Error while Uploading the package. Hence deleting the package ")
            Report_file.add_line("Error while Uploading the package. Hence deleting the package ")
            delete_cnf_nsd_packages(i, "TOSCA CNFD")

        assert False


def fetch_package_details(packages):
    """
    Argument:
       packages = List of package names in ECM
       Example: ['spider-app-multi-a-1.0.2', 'spider-app-multi-b-1.0.2']
    """
    conn = None
    try:
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        if is_cloudnative:
            table_data = get_ecm_package_list()
        else:
            log.info('Start fetching package ids from RDB')
            Report_file.add_line('Start fetching package ids from RDB')
            ecm_gui_username = Ecm_core.get_ecm_gui_username(Ecm_core)
            rdb_vm_ip = Ecm_PI.get_rdb_vm_ip(Ecm_PI)
            db_password = Common_utilities.fetch_cmdb_password(Common_utilities)
            log.info('connecting with database to fetch the data')
            conn = get_PSQL_connection(rdb_vm_ip, 'ecmdb1', 'cmdb', db_password)
            table_data = get_table_data_from_PSQL_table_for_ecm_package_deletion(conn, 'id', 'package_format',
                                                                                 'is_enabled', 'name',
                                                                                 'cm_package', 'created_by',
                                                                                 ecm_gui_username)
        log.info('ECM package details - :%s', str(table_data))

        output = []
        if not table_data:
            for package_name in packages:
                log.info('Table data is empty. On- boarding package - %s', package_name)
                res = False, '', package_name
                output.append(res)
            return output
        else:
            for package_name in packages:
                val = True
                for record in table_data:
                    if package_name in record:
                        if 'Y' in record[2]:
                            log.info('Package already on-boarded. %s', package_name)
                            res = True, '', package_name
                            output.append(res)
                        else:
                            log.info('Package created with status as N. %s', package_name)
                            package_id = record[0]
                            res = False, package_id, package_name
                            output.append(res)
                        val = False
                if val:
                    log.info('Package not found in ECM package list/RDB. On- boarding package - %s', package_name)
                    res = False, '', package_name
                    output.append(res)
            return output
    except Exception as e:
        log.error('Error While fetching package details %s', str(e))
        Report_file.add_line('Error while fetching package details' + str(e))
        assert False
    finally:
        if conn:
            conn.close()


def onboard_packages_in_parallel(json_filename, pkgs_dir_path, packages_name_list):
    ecm_connection = None
    try:
        log.info('Starting to onboard packages in parallel.')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        id_list = []
        package_count = 1
        pkg_count = 1
        thread_pool_pkg = []
        for cnf_package_name in packages_name_list:
            pkg_name = cnf_package_name + ".csar"
            log.info('Onboarding package-%s', pkg_name)
            log.info('Making ecm connection')
            new_json_file = 'createpackage' + str(package_count) + '.json'
            package_count = package_count + 1
            with open(json_filename, "r") as jsonfile:
                json_file_data = json.load(jsonfile)
                Json_file_handler.update_json_file(Json_file_handler, new_json_file, json_file_data)
            update_cnf_create_package_file(new_json_file, cnf_package_name, pkg_name)
            log.info('Making ecm connection')
            ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            log.info('Transferring %s file to blade host server', new_json_file)
            ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + new_json_file,
                                           SIT.get_base_folder(SIT) + new_json_file)

            time.sleep(2)
            token = Common_utilities.authToken(Common_utilities, ecm_connection, core_vm_hostname)
            command = '''curl --insecure "https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages" -H "Accept: application/json" -H "Content-Type: application/json" -H 'AuthToken: {}' --data @{}'''.format(
                core_vm_hostname, token, new_json_file)
            output = Common_utilities.execute_curl_command(Common_utilities, ecm_connection, command)
            log.info("Curl command output: %s", str(output))

            if 'onboardingState' in output.keys():
                if output['onboardingState'] == 'CREATED':
                    vnf_instance_id = output['id']
                    log.info('Create CNF package vnf_descriptors_id - %s', vnf_instance_id)
                    id_list.append(vnf_instance_id)
                    thread = threading.Thread(target=upload_cnf_package, name='Thread_' + str(pkg_count),
                                              args=(ecm_connection, token, vnf_instance_id, core_vm_hostname,
                                                    pkg_name, pkgs_dir_path, id_list))
                    thread_pool_pkg.append(thread)
                    pkg_count = pkg_count + 1
                else:
                    log.info('CNF package status %s', output['onboardingState'])
            else:
                log.error('Error in Create CNF package %s', str(cnf_package_name))
                assert False

        log.info(thread_pool_pkg)
        for task in thread_pool_pkg:
            task.start()
        for task in thread_pool_pkg:
            task.join()
    except Exception as error:
        log.error('Error While creating CNF package %s', str(error))
        ecm_connection.close()
        assert False


def upload_tosca_cnf_package(pkgs_dir_path):
    ecm_connection = None
    try:
        log.info('Start to create CNF package')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        pkg_name_pattern = "*.csar"
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        json_filename = r'com_ericsson_do_auto_integration_files/' + 'createpackage.json'
        command = 'find {} -name {}{}{}'.format(pkgs_dir_path, '"', pkg_name_pattern, '"')
        stdin, stdout, stderr = ecm_connection.exec_command(command)
        command_output = str(stdout.read())[2:-3:]
        output = command_output.split('\\n')
        ecm_connection.close()
        packages_name_list = []

        cnf_packages = [package.split(pkgs_dir_path)[1].split(".csar")[0] for package in output]
        package_details = fetch_package_details(cnf_packages)
        log.info('Package details from DB %s', str(package_details))
        for pkg_detail in package_details:
            is_enabled, package_id, pkg_name = pkg_detail
            if not is_enabled:
                if package_id != '':
                    log.info('Deleting package as its status is N in rdb - %s', pkg_name)
                    log.info('Deleting package id - %s', package_id)
                    delete_node_vnf_package(package_id)
                packages_name_list.append(pkg_name)
            else:
                log.info('Package already on-boarded as its status in rdb is Y - %s', pkg_name)

        if packages_name_list:
            onboard_packages_in_parallel(json_filename, pkgs_dir_path, packages_name_list)
            print_cnf_package_report()

    except Exception as e:
        log.error('Error While creating CNF package %s', str(e))
        ecm_connection.close()
        assert False


def cnf_nsd_package_details():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    pkgs_dir_path = sit_data._SIT__cnfconfigmapSoftwarePath
    package = 'nsd-cnf.zip'
    packageName = package.split('.zip')[0]
    filename = 'createNSDpackage.json'
    return pkgs_dir_path, package, packageName, filename


def create_cnfns_nsd_package():
    try:
        pkgs_dir_path, package, packageName, filename = cnf_nsd_package_details()
        create_nsd_package(packageName, filename)
    except Exception as e:
        log.error('Error While creating CNF NSD package ' + str(e))
        Report_file.add_line('Error while creating CNF NSD package ' + str(e))
        assert False


def upload_cnfns_nsd_package():
    try:
        pkgs_dir_path, package, packageName, filename = cnf_nsd_package_details()
        upload_nsd_package(pkgs_dir_path, package)
    except Exception as e:
        log.error('Error While uploading CNF NSD package ' + str(e))
        Report_file.add_line('Error while uploading CNF NSD package ' + str(e))
        assert False


def create_cnf_ns():
    try:
        # log.info('Start to create CNF NS package')
        # Report_file.add_line(Report_file, 'Start to create CNF NS package')
        create_ns_package()
    except Exception as e:
        log.error('Error While creating CNF NS package ' + str(e))
        Report_file.add_line('Error while creating CNF NS package ' + str(e))
        assert False


def installation_of_cnfns():
    try:
        # log.info('Start to install NS CNF')
        # Report_file.add_line(Report_file, 'Start to install NS CNF')
        instantiate_ns()
    except Exception as e:
        log.error('Failed to install CNF NS ' + str(e))
        Report_file.add_line('Failed to install CNF NS ' + str(e))
        assert False


def create_ns_package():
    log.info('Start to create NS package')
    Report_file.add_line('Start to create NS package')
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        json_file = 'createNS.json'

        nsdId, nsdName = fetch_nsd_details(connection, core_vm_hostname)
        update_ns_create_package_file(json_file, nsdId, nsdName)
        log.info('Transferring ' + json_file + ' file to blade host server ')

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + json_file,
                                       SIT.get_base_folder(SIT) + json_file)

        time.sleep(2)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        curl_command = '''curl --insecure https://{}/ecm_service/SOL005/nslcm/v1/ns_instances -H "Content-Type: application/json" -H "AuthToken: {}" --data @{}'''.format(
            core_vm_hostname, token, json_file)
        output = Common_utilities.execute_curl_command(Common_utilities, connection, curl_command)
        if 'Error' in output or 'Failure' in output or 'Invalid' in output:
            Report_file.add_line('Error while creating NS package ')
            assert False
        global ns_instances_id
        ns_instances_id = output['id']
        Report_file.add_line('Create NS package instances id - ' + ns_instances_id)

    except Exception as e:
        log.error('Error While creating NS package ' + str(e))
        Report_file.add_line('Error while creating NS package ' + str(e))
        assert False
    finally:
        connection.close()


def instantiate_ns():
    log.info('Start to create NS Instantiate')
    Report_file.add_line('Start to create NS Instantiate')
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        file_name = 'instantiatecnf.json'
        nsd_id, nsdName = fetch_nsd_details(connection, core_vm_hostname)
        update_cnf_instanatiate_file(file_name, nsdName)
        log.info('Transferring ' + file_name + ' file to blade host server ')

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)
        time.sleep(2)
        curl_command = '''curl --insecure -i -X POST "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}/instantiate" -H "AuthToken: {}" -H "Content-Type: application/json" --data @{}'''.format(
            core_vm_hostname, ns_instances_id, token, file_name)
        command_output = ExecuteCurlCommand.get_json_output(connection, curl_command)

        Report_file.add_line('command output : ' + command_output)
        output = command_output

        if '202 Accepted' in output:
            orderid = output.split('\\r\\n')[5]
            order_id = orderid.split(': ')[1]
            log.info('Instantiate NS Order Id - ' + order_id)
            Report_file.add_line('Instantiate NS Order Id -' + order_id)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            order_status, order_output = Common_utilities.NSorderReqStatus(Common_utilities, connection,
                                                                           token, core_vm_hostname, order_id,
                                                                           10)
            if order_status:
                log.info("Successfully Completed Instantiation of NS")
                Report_file.add_line('Successfully Completed Instantiation of NS')
            else:
                Report_file.add_line(order_output)
                log.error('order status for NS Instantiate has been failed  ' + order_id)
                Report_file.add_line('order status for NS Instantiate has been failed ' + order_id)
                assert False

        else:
            Report_file.add_line('Error in While doing Instantiation of NS')
            assert False

    except Exception as e:
        log.error('Error While doing Instantiate NS ' + str(e))
        Report_file.add_line('Error while doing Instantiate NS ' + str(e))
        log.info("Error while Uploading the package. Hence deleting the package " + ns_instances_id)
        Report_file.add_line(
            "Error while Uploading the package. Hence deleting the package " + ns_instances_id)
        delete_cnf_nsd_packages(ns_instances_id, 'NS-TERMINATE')
        assert False

    finally:
        connection.close()
