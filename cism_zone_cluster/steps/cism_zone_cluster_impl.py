from behave import *
from com_ericsson_do_auto_integration_scripts.CISM_ZONE_CLUSTER import *


##################################EOCM JOB ############################

@step("I start the Scenario to Register CISMS Zone Cluster")
def step_impl(context):
    register_cism_zone()


@step("I start the Scenario to Deregister CISMS Zone Cluster")
def step_impl(context):
    derigester_cism_zone()

##################################EVNFM JOB ############################


@step("I start the Scenario to EVNFM Register CISMS Zone Cluster")
def step_impl(context):
    register_evnfm_cism_zone()


@step("I start the Scenario to EVNFM Deregister CISMS Zone Cluster")
def step_impl(context):
    deregister_evnfm_cism_zone()