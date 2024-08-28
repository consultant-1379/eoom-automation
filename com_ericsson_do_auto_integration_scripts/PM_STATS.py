from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_utilities.kube_exec_it_pod import get_exec_pod_it_command_sql
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
import os


log = Logger.get_logger('PM_STATS.py')

def execute_cmd_and_format_output(director_connection, cmd):
    stdin, stdout, stderr = director_connection.exec_command(cmd)
    return str(stdout.read()).replace("b'","").replace("\\n'","").strip()


def check_pm_stats():

    pm_stats_kpi_pod_name = SIT.get_pm_stats_kpi_pod_name(SIT)
    pm_stats_container_name = SIT.get_pm_stats_container_name(SIT)
    pm_stats_db_user = SIT.get_pm_stats_db_user(SIT)
    pm_stats_db_name = SIT.get_pm_stats_db_name(SIT)
    pm_stats_calc_pod = SIT.get_pm_stats_calc_pod(SIT)
    pm_stats_calc_container = SIT.get_pm_stats_calc_container(SIT)
    so_namespace = SIT.get_so_namespace(SIT)
    try:
        director_connection = get_VMVNFM_host_connection()
        sql_count_states = get_exec_pod_it_command_sql(so_namespace,
                                                       pm_stats_kpi_pod_name,
                                                       pm_stats_container_name,
                                                       pm_stats_db_user,
                                                       pm_stats_db_name,
                                                       "select count(state) from kpi_calculation;")
        log.info("Getting count of states with: " + sql_count_states)
        command_output = execute_cmd_and_format_output(director_connection, sql_count_states)
        total_states = int(command_output)
        if total_states == 0:
            assert False
        sql_count_bad_states = get_exec_pod_it_command_sql(so_namespace,
                                                           pm_stats_kpi_pod_name,
                                                           pm_stats_container_name,
                                                           pm_stats_db_user,
                                                           pm_stats_db_name,
                                                           "select count(state) from kpi_calculation "\
                                                           "where state in ('LOST', 'FAILED', 'SENDING_TO_EXPORTER');")
        log.info("Getting count of bad states with: " + sql_count_bad_states)
        command_output = execute_cmd_and_format_output(director_connection, sql_count_bad_states)
        total_bad_states = int(command_output)
        log.info("\n\tBad States: " + str(total_bad_states) + "\n\tTotal States: " + str(total_states))
        ratio = round((total_bad_states/total_states)*100, 2)
        log.info("Ratio of bad states against total states is " + str(ratio) + "%")
        if ratio >= 10:
            pod_name = execute_cmd_and_format_output(director_connection, f"kubectl -n {so_namespace} get pods |grep"
                                                                          f" {pm_stats_calc_pod}|"\
                                                                          "awk '{print$1}'")
            log.info("POD NAME = " + pod_name)
            stdin, stdout, stderr = director_connection.exec_command(
                f"kubectl -n {so_namespace} logs {pod_name} -c {pm_stats_calc_container} --since 1h"
            )
            pod_logs = str(stdout.read()).replace("\\n", "\n")
            log.info(f"Error: Logs for {pod_name}:")
            log.info(pod_logs)
            assert False
        elif (ratio >= 5) and (ratio < 10):
            log.info("Bad state ratio is equal or greater than 5% but smaller than 10!!!")
            log.info(f"Test Passed with a ratio of: {ratio}")
        else:
            log.info("Test Passed!!!")
    except Exception as e:
        if total_states == 0:
            log.error("ERROR: There is no states in the DB")
        else:
            log.error("ERROR: Ratio of bad states against total of states is 10% or more")
        assert False
