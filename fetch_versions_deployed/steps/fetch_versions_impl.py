from behave import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *


@given(u'I start the Scenario to fetch deployed versions')
def step_impl(context):
    fetch_deployed_versions()
