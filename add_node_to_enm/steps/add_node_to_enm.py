from behave import *
from com_ericsson_do_auto_integration_scripts.ADD_NODE_TO_ENM import add_nodes_to_ENM

@step("I start the Scenario to add a node to ENM")
def step_impl(context):
    add_nodes_to_ENM()