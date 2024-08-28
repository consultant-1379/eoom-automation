from behave import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.PM_STATS import check_pm_stats

log = Logger.get_logger('kpi_calculations_on_service_db_impl.py')

@step("I start the Scenario to Verify the calculations on pm-stats")
def step_impl(context):

    check_pm_stats()
