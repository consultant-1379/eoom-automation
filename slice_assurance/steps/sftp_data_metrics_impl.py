from behave import *

from com_ericsson_do_auto_integration_scripts.SFTP_DATA_METRICS_VERIFICATIONS import fetching_SFTP_data_metrics, \
    fetch_core_parser_metrics, list_minio_bucket_objects


@step("I start the Scenario to check the data flow metrics on the sftp pod")
def step_impl(context):
    fetching_SFTP_data_metrics()

@step("I start the Scenario to check the file collection on the miniodb")
def step_impl(context):
    list_minio_bucket_objects()

@step("I start the Scenario to check the data flow metrics on the core parser pod")
def step_impl(context):
    fetch_core_parser_metrics()





