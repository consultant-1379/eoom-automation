
from behave import *
from com_ericsson_do_auto_integration_scripts.Start_netsim import connect_to_netsim_server

@step("I start the Scenario to start activating the node on the netsim")
def step_impl(context):
    connect_to_netsim_server()
