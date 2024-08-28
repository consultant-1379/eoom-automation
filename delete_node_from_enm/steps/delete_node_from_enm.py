from behave import step
from com_ericsson_do_auto_integration_scripts.DELETE_NODE_FROM_ENM import delete_nodes_from_ENM 


@step("I start the Scenario to delete a node from ENM")
def step_impl(context):

    # Assume that a previous job would invoke this fn to delete a list of nodes
    # In which case, this function would need to be modified to support that
    delete_nodes_from_ENM()