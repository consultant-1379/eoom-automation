from behave import *

from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import verify_cism_cluster_exists
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('ccm_cism_verification_impl.py')


@step("I start the Scenario to verify cism cluster exists in ccm")
def step_impl(context):
    verify_cism_cluster_exists()
