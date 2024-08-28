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
import ast
import json
import time
import requests
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_utilities import UDS_PROPERTIES as constants
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.CURL_UDS_VNF_SERVICE import CurlUdsVnfService
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import onboard_enm_ecm_subsystems
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_import_vsp_as_vf_json_file,
                                                                         update_add_vf_to_vnf_service_json_file)
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('UDS_STATIC_METHODS.py')


class UdsOperations:

    @staticmethod
    def submit_vlm(connection_ecm, uds_token, item_id, version_id):
        try:
            log.info('Starting to submit the  VLM :::')
            ServerConnection.put_file_sftp(connection_ecm,
                                           constants.VLM['submit_vlm_source_path'],
                                           constants.VLM['submit_vlm_destination_path'])
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            cmd = CurlUdsVnfService.submit_vlm_curl(uds_token, uds_hostname, item_id, version_id)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(connection_ecm, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl Response ::: %s", out)
            if out == '{}':
                log.info('Successfully submitted the VLM :::')
            else:
                log.info('Failed to submit the VLM :::')
                assert False
        except Exception as e:
            log.error('Error While creating the VLM ::: %s', str(e))
            assert False

    @staticmethod
    def attach_package(uds_token, blade_connection, item_id, version_id):
        try:
            log.info('Starting to attach the package :::')
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            software_path = sit_data._SIT__uds_cm_package_path
            file_name = software_path + constants.PACKAGE_NAME
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            cmd = CurlUdsVnfService.attach_package_curl(uds_token, uds_hostname, item_id, version_id, file_name)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(blade_connection, cmd)
            log.info("Curl Output ::: %s", out)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info("Curl Output ::: %s", out)
            if out["status"] == "Success":
                log.info('Successfully attached the package :::')
            else:
                log.info('Failed to attached the package ::: %s', str(out["error"]))
                assert False
        except Exception as e:
            log.error('Error While attaching package ::: %s', str(e))
            assert False

    @staticmethod
    def submit_vsp(blade_server_connection, uds_token, item_id, version_id):
        try:
            log.info('Starting to submit the VSP :::')
            ServerConnection.put_file_sftp(blade_server_connection, constants.VSP['submit_vsp_source_path'],
                                           constants.VSP['submit_vsp_destination_path'])
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            cmd = CurlUdsVnfService.submit_vsp_curl(uds_token, uds_hostname, item_id, version_id)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(blade_server_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl Output ::: %s", out)
            if '200 OK' in out or out == '':
                log.info('Successfully submitted the VSP :::')
            else:
                log.info('Failed to submit the VSP :::')
                assert False
        except Exception as e:
            log.error('Error While submitting the VSP ::: %s', str(e))
            assert False

    @staticmethod
    def import_vsp_as_vf(new_connection, uds_token, vspname, item_id, version_id, vendorname):
        try:
            log.info('Starting to import VSP as VF :::')
            vsp_name_value = vspname.replace('-', '').lower()
            file_name = constants.VSP_AS_VF['import_vsp_file']
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            update_import_vsp_as_vf_json_file(file_name, item_id, version_id, vendorname, vspname)
            MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities,
                                                                       constants.VSP_AS_VF['import_vsp_source_path'])
            ServerConnection.put_file_sftp(new_connection, constants.VSP_AS_VF['import_vsp_source_path'],
                                           constants.VSP_AS_VF['import_vsp_destination_path'])
            cmd = CurlUdsVnfService.import_vsp_as_vf_curl(uds_token, uds_hostname, MD5_code)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(new_connection, cmd)
            log.info("Curl Output ::: %s", out)
            ServerConnection.get_file_sftp(new_connection, constants.VSP_AS_VF['result_source'],
                                           constants.VSP_AS_VF['result_destination'])
            out = out[2:-1:1]
            value = f'''vsp{vsp_name_value}informationtxt'''
            f = open(constants.VSP_AS_VF['result_destination'], 'r')
            data = json.loads(f.read())
            log.info(data)
            if data:
                id = data['uniqueId']
                id = id.split('.')[0]
                log.info('VSP as VF unique ID ::: %s', str(id))
                certify_vf_unique_id = UdsOperations.certify_vf(new_connection, uds_token, id)
                return certify_vf_unique_id
            else:
                log.info('Failed to import VSP as VF :::')
                assert False
        except Exception as e:
            log.error('Error While importing VSP as VF ::: %s', str(e))
            assert False

    @staticmethod
    def certify_vf(new_connection, uds_token, vsp_as_vf_unique_id):
        try:
            log.info('Starting to certify the VF :::')
            ServerConnection.put_file_sftp(new_connection, constants.VSP_AS_VF['certify_vf_source_path'],
                                           constants.VSP_AS_VF['certify_vf_destination_path'])
            global certify_vf_unique_id
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            cmd = CurlUdsVnfService.certify_vf_curl(uds_token, uds_hostname, vsp_as_vf_unique_id)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(new_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info("Curl Output ::: %s", out)
            if 'uniqueId' in out:
                certify_vf_unique_id = out["uniqueId"]
                certify_vf_unique_id = certify_vf_unique_id.split('.')[0]
                log.info(certify_vf_unique_id)
                log.info('Successfully certified the VF :::')
                return certify_vf_unique_id
            else:
                log.info('Failed to certify the VF :::')
                assert False
        except Exception as e:
            log.error('Error While certifying the VF ::: %s', str(e))
            assert False

    @staticmethod
    def add_vf_to_vnf_service(uds_token, ecm_connection, vnf_service_unique_id):
        try:
            log.info('Starting to add vf to vnf service :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            file_name = constants.VNF_SERVICE['add_vnf_service_file']
            update_add_vf_to_vnf_service_json_file(file_name, certify_vf_unique_id)
            ServerConnection.put_file_sftp(ecm_connection, constants.VNF_SERVICE['add_vnf_service_source_path'],
                                           constants.VNF_SERVICE['add_vnf_service_destination_path'])
            cmd = CurlUdsVnfService.add_vf_to_service_curl(uds_token, uds_hostname, vnf_service_unique_id)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(ecm_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl Output ::: %s", out)
            if '201 Created' in out:
                log.info('Successfully added vf to vnf service :::')
                certify_service_unique_id = UdsOperations.certify_service(vnf_service_unique_id)
                return certify_service_unique_id
            else:
                log.info('Failed to add vf to vnf service :::')
                assert False
        except Exception as e:
            log.error('Error While adding vf to vnf service ::: %s', str(e))
            assert False

    @staticmethod
    def certify_service(vnf_service_unique_id):
        new_ecm_server_connection = None
        try:
            log.info('Starting to certify service :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            new_ecm_server_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, new_ecm_server_connection, uds_hostname,
                                                            uds_username, uds_password, constants.TENANT)
            file_name = constants.VNF_SERVICE['certify_vnf_file']
            ServerConnection.put_file_sftp(new_ecm_server_connection,
                                           constants.VNF_SERVICE['certify_vnf_source_path'],
                                           constants.VNF_SERVICE['certify_vnf_destination_path'])
            cmd = CurlUdsVnfService.certify_service_curl(uds_token, uds_hostname, vnf_service_unique_id)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(new_ecm_server_connection, cmd)
            log.info("Curl Output ::: %s", out)
            source = constants.VNF_SERVICE['out_certify_source']
            destination = constants.VNF_SERVICE['out_certify_destination']
            ServerConnection.get_file_sftp(new_ecm_server_connection, source, destination)
            f = open(constants.VNF_SERVICE['out_certify_destination'], 'r')
            data = json.loads(f.read())
            log.info(data)
            if 'uniqueId' in data:
                certify_service_unique_id = data["uniqueId"]
                certify_service_unique_id = certify_service_unique_id.split('.')[0]
                log.info(certify_service_unique_id)
                log.info('Successfully certified service :::')
                UdsOperations.distribute_service(certify_service_unique_id)
                return certify_service_unique_id
            else:
                log.info('Failed to certify service :::')
                new_ecm_server_connection.close()
                assert False
        except Exception as e:
            log.error('Error While certifying service ::: %s', str(e))
            assert False
        finally:
            new_ecm_server_connection.close()

    @staticmethod
    def onboarding_so_subsytems():

        onboard_enm_ecm_subsystems('subsystem')

    @staticmethod
    def distribute_service(certify_service_unique_id):
        connection_with_ecm = None
        try:
            log.info('Starting to distribute service :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection_with_ecm = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection_with_ecm, uds_hostname,
                                                            uds_username, uds_password, 'master')
            _ = UdsOperations.check_connected_systems(connection_with_ecm, uds_token, uds_hostname)

            url = f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{certify_service_unique_id}/distribution/PROD/activate"
            response = requests.post(url=url, headers={"cookie": f'JSESSIONID={uds_token}',
                                                       "Content-Type": "application/json",
                                                       "USER_ID": "cs0008"}, verify=False)
            if response.status_code == 200:
                response = response.json()
                time.sleep(60)
                distribution_flag = UdsOperations.check_distribution_status(uds_token, uds_hostname, response['uuid'])
                if distribution_flag:
                    log.info('Successfully distributed service :::')
                else:
                    log.info('Failed to distribute service :::')
                    assert False
            else:
                log.info('Failed to distribute service :::')
                assert False
        except Exception as e:
            log.error('Error While distributing service ::: %s', str(e))
            assert False
        finally:
            connection_with_ecm.close()

    @staticmethod
    def check_connected_systems(connection, token, hostname):
        try:
            log.info('Starting to check the connected systems in UDS :::')
            cmd = CurlUdsVnfService.check_connected_systems_curl(token, hostname)
            log.info("Curl Command ::: %s", cmd)
            out = ExecuteCurlCommand.get_json_output(connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = out.split('envoy')
            out = out[-1]
            log.info("Curl Output ::: %s", out)
            if 'connectionProperties' in out:
                return True
            else:
                constants.CONNECTION_REQUEST['connectionProperties'][0]['username'] = \
                    Ecm_core.get_ecm_gui_username(Ecm_core)
                constants.CONNECTION_REQUEST['connectionProperties'][0]['password'] = \
                    Ecm_core.get_ecm_gui_password(Ecm_core)
                constants.CONNECTION_REQUEST['url'] = f'https://{Ecm_core.get_core_vm_hostname(Ecm_core)}'
                cmd = CurlUdsVnfService.establish_connection(token, hostname, constants.CONNECTION_REQUEST)
                log.info("Curl Command ::: %s", cmd)
                out = ExecuteCurlCommand.get_json_output(connection, cmd)
                out = ExecuteCurlCommand.get_sliced_command_output(out)
                log.info("Curl Output ::: %s", out)
                if out:
                    return True
                else:
                    assert False
        except Exception as e:
            log.error(f"Exception occurred while checking connected systems ::: {e}")
            assert False

    @staticmethod
    def update_uds_nfv_service_properties(token, service_id):
        try:
            log.info('Inside the update uds nfv service template properties :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            url = f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{service_id}/properties"
            constants.UDS_NFV_SERVICE_PROPERTIES[0]["parentUniqueId"] = service_id
            constants.UDS_NFV_SERVICE_PROPERTIES[0]["uniqueId"] = service_id + ".flavour_id"
            constants.UDS_NFV_SERVICE_PROPERTIES[0]["toscaPresentation"]["ownerId"] = service_id
            log.info(constants.UDS_NFV_SERVICE_PROPERTIES)
            response = requests.put(url=url, headers={"cookie": f'JSESSIONID={token}',
                                                      "Content-Type": "application/json",
                                                      "USER_ID": "cs0008"},
                                    data=json.dumps(constants.UDS_NFV_SERVICE_PROPERTIES), verify=False)
            if response.status_code == 200:
                return True
            else:
                log.info(f"Failure response received from update properties for NFV service :::{response.text}")
                assert False
        except Exception as e:
            log.error(f"Exception occurred while checking connected systems ::: {e}")
            assert False

    @staticmethod
    def check_distribution_status(token, host_name, unique_id):
        try:
            log.info("Check service distribution status :::")
            headers = {"cookie": f'JSESSIONID={token}', "Content-Type": "application/json", "USER_ID": "cs0008"}
            distribution_url = f'https://{host_name}/sdc1/feProxy/rest/v1/catalog/services/{unique_id}/distribution'
            response = requests.get(url=distribution_url, headers=headers, verify=False)
            response = response.json()
            status_url = f'https://{host_name}/sdc1/feProxy/rest/v1/catalog/services/distribution/' \
                         f'{response["distributionStatusOfServiceList"][0]["distributionID"]}'
            count = 0
            flag = True
            while flag:
                out = requests.get(url=status_url, headers=headers, verify=False)
                out = out.json()
                log.info(f'Response of Distribution status check api ::: {out}')
                for data in out['distributionStatusList']:
                    if data['status'] == "COMPONENT_DONE_OK":
                        return True
                    elif data['status'] == "COMPONENT_DONE_ERROR":
                        return False
                count = count + 1
                if count == 7:
                    return False
                else:
                    time.sleep(60)
        except Exception as e:
            log.error(f'Exception occurred while checking the status of distribution ::: {e}')
            return False
