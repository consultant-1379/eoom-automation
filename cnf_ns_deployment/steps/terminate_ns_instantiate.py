
from behave import *
from com_ericsson_do_auto_integration_scripts.ECM_SERVICE_TERMINATE import *


@step("I start the Scenario to Terminate the NS Instantiate")
def step_impl(context):
    terminate_ns_instantiate()
    











