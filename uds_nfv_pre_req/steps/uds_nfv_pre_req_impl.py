from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_VNF_PRE_REQ import UdsVnfPreReq

@step("I start the Scenario to Create VLM and Submit VLM")
def step_impl(context):
    UdsVnfPreReq.create_vlm(UdsVnfPreReq)

@step("I start the Scenario to Create VSP and Attach Package")
def step_impl(context):
    UdsVnfPreReq.create_vsp(UdsVnfPreReq)

@step("I start the Scenario to Process VSP")
def step_impl(context):
    UdsVnfPreReq.process_vsp(UdsVnfPreReq)

@step("I start the Scenario to Commit VSP and Submit VSP")
def step_impl(context):
    UdsVnfPreReq.commit_vsp(UdsVnfPreReq)

@step("I start the Scenario to Create VSP Package Import VSP as VF and Certify VF")
def step_impl(context):
    UdsVnfPreReq.create_vsp_package(UdsVnfPreReq)

@step("I start the Scenario to Create NFV Service Add VF to NFV Service Certify Service and Distribute Service")
def step_impl(context):
    UdsVnfPreReq.create_vnf_service(UdsVnfPreReq, True)

