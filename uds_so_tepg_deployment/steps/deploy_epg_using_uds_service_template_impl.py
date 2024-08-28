from behave import step
from com_ericsson_do_auto_integration_scripts.EPG_TOSCA_SO_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *


@step("I start the Scenario to Create App Network Service for EPG deployment using UDS service template")
def step_impl(context):
    create_uds_so_tepg_network_service(is_esoa=True, is_stub=True)


@step("I start the Scenario of Polling the state of App network service using service ID")
def step_impl(context):
    verify_epg_tosca_service_status(is_esoa=True)
