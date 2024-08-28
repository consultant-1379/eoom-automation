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
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.CURL_UDS_VNF_SERVICE import CurlUdsVnfService
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_create_vlm_json_file,
                                                                         update_create_vsp_json_file,
                                                                         update_create_vnf_service_json_file)
from com_ericsson_do_auto_integration_utilities import UDS_PROPERTIES as Constants
from com_ericsson_do_auto_integration_utilities.UDS_STATIC_METHODS import UdsOperations


log = Logger.get_logger('UDS_VNF_PRE_REQ.py')


class UdsVnfPreReq:
    environment = Server_details.ecm_host_blade_env(Server_details)
    data_file = f'com_ericsson_do_auto_integration_files/run_time_{environment}.json'
    source = f'/root/run_time_{environment}.json'

    def create_vlm(self):
        connection_ecm = None
        try:
            log.info('Starting to Create VLM :::')
            file_name = Constants.VLM["create_vlm_file"]
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection_ecm = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection_ecm, uds_hostname,
                                                            uds_username, uds_password, 'master')
            global vendor_name
            vendor_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Ericsson')
            vendor_name = vendor_name.replace('_', '')
            vendor_name = vendor_name.replace('-', '')
            update_create_vlm_json_file(file_name, vendor_name)
            ServerConnection.put_file_sftp(connection_ecm, Constants.VLM["create_vlm_source_path"],
                                           Constants.VLM["create_vlm_destination_path"])
            cmd = CurlUdsVnfService.create_vlm_curl(uds_token, uds_hostname)
            out = ExecuteCurlCommand.get_json_output(connection_ecm, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info(out)
            if "itemId" and "version" in out:
                global vlm_item_id
                item_id = out["itemId"]
                version_id = out["version"]["id"]
                vlm_item_id = item_id
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VLM_ID', item_id)
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VLM_VERSION_ID', version_id)
                log.info('Item ID ::: %s', str(item_id))
                log.info('Version ID ::: %s', str(version_id))
                log.info('VLM Created :::')
                UdsOperations.submit_vlm(connection_ecm, uds_token, item_id, version_id)
            else:
                log.error('Some error encountered While creating the VLM ::: %s', str(out))
                connection_ecm.close()
                assert False
        except Exception as e:
            log.error('Error While creating the VLM ::: %s', str(e))
            assert False
        finally:
            if connection_ecm:
                connection_ecm.close()

    def create_vsp(self):
        blade_connection = None
        try:
            log.info('Starting to Create VSP :::')
            file_name = Constants.VSP["create_vsp_file"]
            global vspName
            vspName = Common_utilities.get_name_with_timestamp(Common_utilities, 'ETSI_TOSCA_VSP')
            vspName = vspName.replace('_', '')
            vspName = vspName.replace('-', '')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, blade_connection, uds_hostname,
                                                            uds_username, uds_password, 'master')
            update_create_vsp_json_file(file_name, vendor_name, vspName, vlm_item_id)
            ServerConnection.put_file_sftp(blade_connection, Constants.VSP["create_vsp_source_path"],
                                           Constants.VSP["create_vsp_destination_path"])
            cmd = CurlUdsVnfService.create_vsp_curl(uds_token, uds_hostname)
            out = ExecuteCurlCommand.get_json_output(blade_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info(out)
            global item_id
            global version_id
            if "itemId" and "version" in out:
                item_id = out["itemId"]
                version_id = out["version"]["id"]
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VSP_ID', item_id)
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VSP_VERSION_ID', version_id)
                log.info('Item ID ::: %s', str(item_id))
                log.info('Version ID ::: %s', str(version_id))
                log.info('VSP Created :::')
                UdsOperations.attach_package(uds_token, blade_connection, item_id, version_id)
            else:
                log.error('Some error encountered While creating the VSP ::: %s', str(out))
                blade_connection.close()
                assert False
        except Exception as e:
            log.error('Error While creating the VSP ::: %s', str(e))
            assert False
        finally:
            if blade_connection:
                blade_connection.close()

    def process_vsp(self):
        ecm_blade_connection = None
        try:
            log.info('Starting to process VSP :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            ecm_blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, ecm_blade_connection, uds_hostname,
                                                            uds_username, uds_password, 'master')
            ServerConnection.put_file_sftp(ecm_blade_connection, Constants.VSP["process_vsp_source_path"],
                                           Constants.VSP["process_vsp_destination_path"])
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            cmd = CurlUdsVnfService.process_vsp_curl(uds_token, uds_hostname, item_id, version_id)
            out = ExecuteCurlCommand.get_json_output(ecm_blade_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info(out)
            if out["status"] == "Success":
                log.info('Successfully processed VSP :::')
            else:
                log.info('Failed to process VSP ::: %s', str(out["error"]))
                assert False
        except Exception as e:
            log.error('Error While process VSP ::: %s', str(e))
            assert False
        finally:
            if ecm_blade_connection:
                ecm_blade_connection.close()

    def commit_vsp(self):
        blade_server_connection = None
        try:
            log.info('Starting to commit the VSP :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            blade_server_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, blade_server_connection, uds_hostname,
                                                            uds_username, uds_password, 'master')
            ServerConnection.put_file_sftp(blade_server_connection, Constants.VSP['commit_vsp_source_path'],
                                           Constants.VSP['commit_vsp_destination_path'])
            cmd = CurlUdsVnfService.commit_vsp_curl(uds_token, uds_hostname, item_id, version_id)
            out = ExecuteCurlCommand.get_json_output(blade_server_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info(out)
            if '200 OK' in out or out == '':
                log.info('Successfully committed the VSP :::')
                UdsOperations.submit_vsp(blade_server_connection, uds_token, item_id, version_id)
            else:
                log.info('Failed to commit the VSP :::')
                blade_server_connection.close()
                assert False
        except Exception as e:
            log.error('Error While committing the VSP ::: %s', str(e))
            assert False
        finally:
            if blade_server_connection:
                blade_server_connection.close()

    def create_vsp_package(self):
        new_connection = None
        try:
            log.info('Starting to create VSP package :::')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            new_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, new_connection, uds_hostname,
                                                            uds_username, uds_password, 'master')
            ServerConnection.put_file_sftp(new_connection, Constants.VSP["create_vsp_package_source_path"],
                                           Constants.VSP["create_vsp_package_destination_path"])
            cmd = CurlUdsVnfService.create_vsp_package_curl(uds_token, uds_hostname, item_id, version_id)
            out = ExecuteCurlCommand.get_json_output(new_connection, cmd)
            log.info(out)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info(out)
            if 'vspName' in out:
                log.info('Successfully created VSP package :::')
                vfc_id = UdsOperations.import_vsp_as_vf(new_connection, uds_token, vspName, item_id, version_id,
                                                           vendor_name)
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VFC_ID', vfc_id)
            else:
                log.info('Failed to create VSP package :::')
                new_connection.close()
                assert False
        except Exception as e:
            log.error('Error While creating VSP package ::: %s', str(e))
            assert False
        finally:
            if new_connection:
                new_connection.close()

    def create_vnf_service(self, is_nfv=False):
        ecm_connection = None
        connection = None
        try:
            log.info('Starting to create VNF service :::')
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, ecm_connection, uds_hostname,
                                                            uds_username, uds_password, 'master')
            if is_nfv:
                file_name = Constants.NFV_SERVICE['nfv_service_file']
                update_create_vnf_service_json_file(file_name, vspName)
                ServerConnection.put_file_sftp(ecm_connection, Constants.NFV_SERVICE['nfv_service_source_path'],
                                               Constants.NFV_SERVICE['nfv_service_destination_path'])
            else:
                file_name = Constants.VNF_SERVICE['vnf_service_file']
                update_create_vnf_service_json_file(file_name, vspName)
                ServerConnection.put_file_sftp(ecm_connection, Constants.VNF_SERVICE['vnf_service_source_path'],
                                               Constants.VNF_SERVICE['vnf_service_destination_path'])
            cmd = CurlUdsVnfService.create_service_curl(uds_token, uds_hostname, file_name)
            out = ExecuteCurlCommand.get_json_output(ecm_connection, cmd)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            out = ast.literal_eval(out)
            log.info(out)
            if 'properties' in out:
                if is_nfv:
                    vnf_service_unique_id = out["properties"][0]["uniqueId"]
                    vnf_service_unique_id = vnf_service_unique_id.split('.')[0]
                    log.info('Unique Id::: %s', vnf_service_unique_id)
                    log.info('Successfully created NFV service :::')
                    UdsOperations.update_uds_nfv_service_properties(uds_token, vnf_service_unique_id)
                else:
                    vnf_service_unique_id = out["uniqueId"]
                    log.info('Unique Id::: %s', vnf_service_unique_id)
                    log.info('Successfully created VNF service :::')
                service_id = UdsOperations.add_vf_to_vnf_service(uds_token, ecm_connection, vnf_service_unique_id)
                Json_file_handler.modify_attribute(Json_file_handler, self.data_file, 'UDS_VNF_OR_NFV_SERVICE_ID',
                                                   service_id)
                connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
                ServerConnection.put_file_sftp(connection, self.data_file, self.source)
            else:
                log.info('Failed to create VNF service :::')
                ecm_connection.close()
                assert False
        except Exception as e:
            log.error('Error While creating VNF service ::: %s', str(e))
            assert False
        finally:
            if connection:
                connection.close()
            if ecm_connection:
                ecm_connection.close()
