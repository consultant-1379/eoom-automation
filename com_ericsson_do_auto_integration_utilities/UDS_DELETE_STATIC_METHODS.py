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
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.UDS_DELETE_CURL_COMMAND import UdsDeleteCurlCommand


log = Logger.get_logger('UDS_DELETE_STATIC_METHODS.py')


class UdsArchiveMethods:
    """
    This class contains all the methods to archive the resources allocated during service template creation
    """
    @staticmethod
    def archive_service(connection, uds_token, uds_hostname, uds_service_id):
        try:
            log.info("Started archiving Service :::")
            curl = UdsDeleteCurlCommand.archive_service_curl(uds_token, uds_hostname, {}, uds_service_id)
            log.info("Curl for archive service ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out:
                log.info('Service failed to archive :::')
                assert False
            else:
                log.info('Service Successfully to archive :::')
        except Exception as e:
            log.error("Exception occurred while archiving Service ::: %s", str(e))
            assert False

    @staticmethod
    def delete_service(connection, uds_token, uds_hostname, uds_service_id):
        try:
            log.info("Started archiving Service :::")
            curl = UdsDeleteCurlCommand.delete_service_curl(uds_token, uds_hostname, uds_service_id)
            log.info("Curl for archive service ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out:
                log.info('Service failed to archive :::')
                assert False
            else:
                log.info('Service Successfully to archive :::')
        except Exception as e:
            log.error("Exception occurred while archiving Service ::: %s", str(e))
            assert False

    @staticmethod
    def archive_vfc(connection, uds_token, uds_hostname, vfc_id):
        try:
            log.info("Started archiving VFC :::")
            curl = UdsDeleteCurlCommand.archive_vfc_curl(uds_token, uds_hostname, {}, vfc_id)
            log.info("Curl for archive vfc ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out:
                log.info('VFC failed to archive :::')
                assert False
            else:
                log.info('VFC Successfully to archive :::')
        except Exception as e:
            log.error("Exception occurred while archiving VFC ::: %s", str(e))
            assert False

    @staticmethod
    def delete_vfc(connection, uds_token, uds_hostname, vfc_id):
        try:
            log.info("Started Deleting VFC :::")
            curl = UdsDeleteCurlCommand.delete_vfc_curl(uds_token, uds_hostname, vfc_id)
            log.info("Curl for delete vfc ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out:
                log.info('VFC failed to delete :::')
                assert False
            else:
                log.info('VFC Successfully deleted :::')
        except Exception as e:
            log.error("Exception occurred while deleting VFC ::: %s", str(e))
            assert False

    @staticmethod
    def archive_vsp(connection, uds_token, uds_hostname, uds_vsp_id):
        try:
            log.info("Started archiving VSP :::")
            curl = UdsDeleteCurlCommand.archive_vsp_curl(uds_token, uds_hostname, {"action": "ARCHIVE"}, uds_vsp_id)
            log.info("Curl for archive vsp ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out == '{}':
                log.info('VSP Successfully archived :::')
            else:
                log.info('VSP failed to archive :::')
                assert False
        except Exception as e:
            log.error("Exception occurred while archiving VSP ::: %s", str(e))
            assert False

    @staticmethod
    def delete_vsp(connection, uds_token, uds_hostname, uds_vsp_id):
        try:
            log.info("Started deleting VSP :::")
            curl = UdsDeleteCurlCommand.delete_vsp_curl(uds_token, uds_hostname, {}, uds_vsp_id)
            log.info("Curl for deleting vsp ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out == '{}':
                log.info('VSP Successfully deleted :::')
            else:
                log.info('VSP failed to delete :::')
                assert False
        except Exception as e:
            log.error("Exception occurred while deleting VSP ::: %s", str(e))
            assert False

    @staticmethod
    def archive_vlm(connection, uds_token, uds_hostname, uds_vlm_id):
        try:
            log.info("Started archiving VLM :::")
            curl = UdsDeleteCurlCommand.archive_vlm_curl(uds_token, uds_hostname, {"action": "ARCHIVE"}, uds_vlm_id)
            log.info("Curl for archive vlm ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out == '{}':
                log.info('VLM Successfully archived :::')
            else:
                log.info('VLM failed to archive :::')
                assert False
        except Exception as e:
            log.error("Exception occurred while archiving VLM ::: %s", str(e))
            assert False

    @staticmethod
    def delete_vlm(connection, uds_token, uds_hostname, uds_vlm_id):
        try:
            log.info("Started deleting VLM :::")
            curl = UdsDeleteCurlCommand.delete_vlm_curl(uds_token, uds_hostname, {}, uds_vlm_id)
            log.info("Curl for deleting vlm ::: %s", curl)
            out = ExecuteCurlCommand.get_json_output(connection, curl)
            out = ExecuteCurlCommand.get_sliced_command_output(out)
            log.info("Curl response ::: %s", out)
            if out == '{}':
                log.info('VLM Successfully deleted :::')
            else:
                log.info('VLM failed to delete :::')
                assert False
        except Exception as e:
            log.error("Exception occurred while deleting VLM ::: %s", str(e))
            assert False


def get_runtime_data(environment, key):
    try:
        log.info("Getting the key value from the runtime file for the key ::: %s", key)
        data_file = f'com_ericsson_do_auto_integration_files/run_time_{environment}.json'
        value = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, key)
        return value
    except Exception as e:
        log.error("Exception occurred while getting data from runtime file ::: %s", str(e))
        assert False
