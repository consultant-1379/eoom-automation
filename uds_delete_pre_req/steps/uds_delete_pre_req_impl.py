from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_DELETE_PRE_REQ import UdsDeleteServiceResources


@step("I start the Scenario to Archive and Delete All Service and VF")
def step_impl(context):
    UdsDeleteServiceResources.uds_service_and_vf_cleanup(UdsDeleteServiceResources)

@step("I start the Scenario to Archive and Delete All VSP and VLM")
def step_impl(context):
    UdsDeleteServiceResources.delete_vsp_and_vlm(UdsDeleteServiceResources)