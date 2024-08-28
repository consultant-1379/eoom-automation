from behave import step

from com_ericsson_do_auto_integration_scripts.CCM_VIM_ZONE_DEREGISTRATION import deregister_vim_zone
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger(__name__)


@step("I start the Scenario to deregister vim zone in ccm")
def step_impl(context):
    deregister_vim_zone()
