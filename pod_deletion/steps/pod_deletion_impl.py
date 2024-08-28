from behave import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *


@given(u'I start the Scenario to delete the Not ready Pods')
def step_impl(context):
    clean_not_ready_pods()