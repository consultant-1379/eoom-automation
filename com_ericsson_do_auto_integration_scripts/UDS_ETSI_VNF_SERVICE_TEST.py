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

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerDetails import ServerDetails
from com_ericsson_do_auto_integration_utilities.CommonUtilities import CommonUtilities
from com_ericsson_do_auto_integration_utilities.CurlUdsVnfService import CurlUdsVnfService
from com_ericsson_do_auto_integration_utilities.ExecCurl import ExecCurl

log = Logger.get_logger('UDS_ETSI_VNF_SERVICE_TEST.py')


def get_uds_connection():
    try:
        log.info("Generating token for UDS Started :::")
        uds_hostname, uds_username, uds_password = ServerDetails.get_uds_host_data()

        uds_token = CommonUtilities.generate_uds_token("uds.ccd-c16b025-iccr.athtem.eei.ericsson.se", uds_username, uds_password, 'master')
        log.info("Token generated for UDS :::: %s", str(uds_token))
        log.info("Generating token for UDS completed")
        return uds_token, uds_hostname
    except Exception as e:
        log.error("Exception occurred while Generating token for UDS ::: %s", str(e))
        assert False

def create_vlm():
    try:
        log.info('Starting to Create VLM..')
        global vendorName
        vendorName = CommonUtilities.get_name_with_timestamp(CommonUtilities, 'Ericsson')
        vendorName = vendorName.replace('_', '')
        vendorName = vendorName.replace('-', '')
        uds_token, uds_hostname = get_uds_connection()
        request_data = {"vendorName": vendorName, "description": "test_delete_3", "iconRef": "icon"}
        curl = CurlUdsVnfService.create_vlm(uds_token, uds_hostname, request_data)
        log.info("curl for create vlm ::: %s", curl)
        output = ExecCurl.exec_curl(curl)
        log.info(output)
        output = ExecCurl.replace_chars(output)
        output = ast.literal_eval(output)
        log.info("response from the curl ::: %s", output)
        if "itemId" and "version" in output:
            global vlm_item_id
            for i in output:
                item_id = output["itemId"]
                version_id = output["version"]["id"]
                vlm_item_id = item_id
            log.info('Item ID: ' + str(item_id))
            log.info('Version ID: ' + str(version_id))
            log.info('VLM Created.')
            submit_vlm(uds_hostname, uds_token, item_id, version_id)
        else:
            log.error('Some error encountered While creating the VLM ' + str(output))
            assert False
    except Exception as e:
        log.error('Error While creating the VLM ' + str(e))
        assert False


def submit_vlm(uds_hostname, uds_token, item_id, version_id):
    try:
        log.info("Submitting VLM ::: %s", item_id)
        request_data = {}
        curl = CurlUdsVnfService.submit_vlm(uds_token, uds_hostname, request_data, item_id, version_id)
        output = ExecCurl.exec_curl(curl)
        log.info(output)
        output = ExecCurl.replace_chars(output)
        output = ast.literal_eval(output)
    except Exception as e:
        log.error("Exception occurred while submitting VLM ::: %s", str(e))


def create_vsp():
    try:
        log.info("VSP Creation started :::")
        global vspName
        vspName = CommonUtilities.get_name_with_timestamp(CommonUtilities, 'ETSI_TOSCA_VSP')
        vspName = vspName.replace('_', '')
        vsprName = vspName.replace('-', '')
    except Exception as e:
        log.error("exception while creating vsp ::: %s", str(e))