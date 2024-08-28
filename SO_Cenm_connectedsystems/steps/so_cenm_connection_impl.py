from behave import *

from com_ericsson_do_auto_integration_scripts.SO_POST_INSTALLATION import establish_cenm_connection
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('so_cenm_connection_impl.py')

@step("I start the Scenario to establish connection with so and Cenm")
def step_impl(context):
    establish_cenm_connection()