
from behave import *
from com_ericsson_do_auto_integration_scripts.Stop_netsim import stop_node_if_started


@step("I start the Scenario to stop the node on the netsim")
def step_impl(context):
    stop_node_if_started()
