from behave import step
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.UDS_ETSI_VNF_SERVICE_TEST import (create_vlm)

log = Logger.get_logger('uds_etsi_vnf_service_impl.py')

@step("I Start The Scenario To Create VLM")
def step_impl(context):
    create_vlm()
    log.info("Testing uds service")
