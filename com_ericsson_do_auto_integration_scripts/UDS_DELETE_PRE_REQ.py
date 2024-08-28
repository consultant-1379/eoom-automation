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
import json
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.UDS_DELETE_CURL_COMMAND import UdsDeleteCurlCommand
from com_ericsson_do_auto_integration_utilities.UDS_CLEANUP_CURL_COMMAND import UdsCleanupCurlCommand
from com_ericsson_do_auto_integration_utilities.UDS_DELETE_STATIC_METHODS import (UdsArchiveMethods, get_runtime_data)

log = Logger.get_logger('UDS_DELETE_PRE_REQ.py')

class UdsDeleteServiceResources:
    """
    This class has all the methods that are used to delete the Service, VFC, VSP, VLM that are attached and created
    during the creation of the given service.
    """
    @staticmethod
    def get_uds_connection():
        try:
            log.info("Creation connection with the UDS")
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection_ecm = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            environment = Server_details.ecm_host_blade_env(Server_details)
            log.info("generating for UDS token")
            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection_ecm, uds_hostname,
                                                            uds_username, uds_password, 'master')
            return connection_ecm, uds_token, uds_hostname, environment
        except Exception as e:
            log.error("Exception occurred while making the connection to UDS ::: %s", str(e))
            assert False

    def uds_service_and_vf_cleanup(self):
        """
        This function takes care of deleting all the services and vfc
        """
        connection_ecm = None
        try:
            log.info("Starting the deletion of service in UDS :::")
            connection_ecm, uds_token, uds_hostname, environment = UdsDeleteServiceResources.get_uds_connection()
            curl = UdsCleanupCurlCommand.get_service_and_vf_dump(uds_token, uds_hostname)
            log.info("Curl for getting dump of service and vf ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection_ecm, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Response for the service and vf curl ::: %s", str(out))
            out = out.replace("False", 'false')
            out = out.replace("True", 'true')
            out = json.loads(out)
            if out:
                if out.get('services'):
                    for service in out.get('services'):
                        service_id = service.get('uniqueId')
                        UdsArchiveMethods.archive_service(connection_ecm, uds_token, uds_hostname, service_id)
                        UdsArchiveMethods.delete_service(connection_ecm, uds_token, uds_hostname, service_id)
                if out.get('resources'):
                    for vfc in out.get('resources'):
                        if vfc.get('actualComponentType').upper() == "VF":
                            vfc_id = vfc.get('uniqueId')
                            UdsArchiveMethods.archive_vfc(connection_ecm, uds_token, uds_hostname, vfc_id)
                            UdsArchiveMethods.delete_vfc(connection_ecm, uds_token, uds_hostname, vfc_id)
                        # Commented below if block as it's creating issue while vfc upgrading
                        # if vfc.get('actualComponentType').upper() == "VFC":
                        #     vfc_id = vfc.get('uniqueId')
                        #     UdsArchiveMethods.archive_vfc(connection_ecm, uds_token, uds_hostname, vfc_id)
        except Exception as e:
            log.error("Exception while deleting the service ::: %s", str(e))
            assert False
        finally:
            connection_ecm.close()

    def delete_vsp_and_vlm(self):
        """
        This function takes care of deleting the vsp and vlm
        """
        connection_ecm = None
        try:
            log.info("Starting the deletion of vsp and vlm in UDS :::")
            connection_ecm, uds_token, uds_hostname, environment = UdsDeleteServiceResources.get_uds_connection()
            curl = UdsCleanupCurlCommand.get_vsp_and_vlm_dump(uds_token, uds_hostname)
            log.info("Curl for getting dump of vsp and vlm ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection_ecm, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Response for the vsp and vlm curl ::: %s", str(out))
            vlm_dump_collection = []
            out = json.loads(out)
            if out.get('results'):
                for record in out.get('results'):
                    if record.get("type").upper() == "VSP":
                        vsp_id = record.get('id')
                        UdsArchiveMethods.archive_vsp(connection_ecm, uds_token, uds_hostname, vsp_id)
                        UdsArchiveMethods.delete_vsp(connection_ecm, uds_token, uds_hostname, vsp_id)
                    if record.get("type").upper() == "VLM":
                        vlm_dump_collection.append(record)
            if vlm_dump_collection:
                for record in vlm_dump_collection:
                    vlm_id = record.get('id')
                    UdsArchiveMethods.archive_vlm(connection_ecm, uds_token, uds_hostname, vlm_id)
                    UdsArchiveMethods.delete_vlm(connection_ecm, uds_token, uds_hostname, vlm_id)
        except Exception as e:
            log.error("Exception while deleting the VSP ::: %s", str(e))
            assert False
        finally:
            connection_ecm.close()
