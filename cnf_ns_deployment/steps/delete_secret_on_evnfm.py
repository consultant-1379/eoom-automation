
from behave import *
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_TERMINATE import *


@step("I start the Scenario to delete Secret on evnfm")
def step_impl(context):
    delete_secret()
    











