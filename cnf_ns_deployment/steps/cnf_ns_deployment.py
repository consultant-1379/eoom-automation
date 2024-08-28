
from behave import *
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *


@step("I start the Scenario to create NSD package")
def step_impl(context):
    create_cnfns_nsd_package()
    

@step("I start the Scenario to upload NSD package into Cloud Manager")
def step_impl(context):
    upload_cnfns_nsd_package()
    
   
@step("I start the Scenario to create NS")
def step_impl(context):
    create_cnf_ns()


@step("I start the Scenario to instantiate NS")
def step_impl(context):
    installation_of_cnfns()













