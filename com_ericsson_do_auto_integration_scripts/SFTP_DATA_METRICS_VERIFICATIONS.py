# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************
import json
import time
import socket
import subprocess
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.UDS_PROPERTIES import SO_CENM_CONNECTION_REQUEST, managed_elements, \
    pmics, metrics_sftp, zero_threshold, greater_than_zero_threshold, metrics_coreparser

log = Logger.get_logger('SFTP_DATA_METRICS_VERIFICATIONS.py')


def fetching_SFTP_data_metrics():
    try:
        director_connection = get_VMVNFM_host_connection()
        so_namespace = SIT.get_so_namespace(SIT)
        output = director_connection.exec_command(f"kubectl get pods -n {so_namespace} | grep eric-oss-sftp-filetrans-core-1-")[1]
        if not output:
            log.error("Error: No pod found with label app=eric-oss-sftp-filetrans-core-1")
            return None
        pod_name = output.read().decode().split()[0]
        timeout = 1500
        poll_interval = 300
        metric_values = {}
        for metric in metrics_sftp:
            metric_found = False  # Flag to indicate if the metric has been found
            while timeout > 0:
                log_command = (
                    f"kubectl logs -n {so_namespace} {pod_name} --since-time=$(date -d '-15 min' -u '+%Y-%m-%dT%H:%M:%SZ') "
                    f"| awk '/{metric.upper()}/ {{print $NF}}' "
                    f"| cut -d ',' -f1 "
                    f"| tr -d '\"'"
                )
                stdin, stdout, stderr = director_connection.exec_command(log_command)
                logs = stdout.read().decode().strip()
                if not logs:
                    log.error(f"Error: Could not fetch metric {metric}")
                    assert False
                metric_value = float(logs)
                metric_values[metric] = logs
                log.info(f"Metric {metric} value: {logs}")
                if metric in zero_threshold and metric_value <= zero_threshold[metric]:
                    if timeout == 0:
                        log.error(f"Error: Metric {metric} value is still zero after 20 minutes")
                        assert False
                    else:
                        log.info(f"Metric {metric} value is zero. Polling again in {poll_interval} seconds.")
                        time.sleep(poll_interval)
                        timeout -= poll_interval
                else:
                    metric_found = True
                    if metric in greater_than_zero_threshold and metric_value > greater_than_zero_threshold[metric]:
                        log.error(f"Error: Metric {metric} value is greater than zero.")
                        assert False
                    break

            if not metric_found:
                log.info(f"Metric {metric} not found within the timeout period")
                assert False

        if timeout == 0:
            log.info('Automation script timed out after 20 minutes')
            assert False

    except ValueError as e:
        log.error(f"Error: Invalid metric value for {e}")
        assert False
    except Exception as e:
        log.error(f"Error fetching SFTP data metrics: {e}")
        assert False

def retrieve_minio_file_listing():
    enm_name = SO_CENM_CONNECTION_REQUEST["name"]
    minio_path = f"minio/{enm_name}/ericsson/{pmics[0]}/XML/5MIN/ManagedElement={managed_elements[0]}/"
    log_file = "file_listing.log"
    command = f"bash -c 'mc ls {minio_path}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        output = stdout.decode("utf-8")
        with open(log_file, "w") as f:
            f.write(output)
        log.info(f"File listing saved to {log_file}")
    else:
        error = stderr.decode("utf-8")
        log.error(f"Error retrieving file listing: {error}")

def list_minio_bucket_objects():
    try:
        # Get the connection to the Minio management pod
        director_connection = get_VMVNFM_host_connection()
    except Exception as e:
        log.error(f"Error connecting to director: {e}")
        return None
      # Get the SO namespace
    so_namespace = SIT.get_so_namespace(SIT)
    # Get the Minio pod name
    output = director_connection.exec_command(f"kubectl get pods -l app=eric-data-object-storage-mn-mgt --field-selector=status.phase=Running -o jsonpath='{{.items[0].metadata.name}}' -n {so_namespace}")[1]
    if not output:
        log.error("Error: No pod found with label app=eric-data-object-storage-mn-mgt")
        return None
    pod_name = output.read().decode().strip()

    # Configure Minio
    config_cmd = "mc config host add minio http://eric-data-object-storage-mn:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY"
    log.info(f"Configuring Minio with command: {config_cmd}")
    stdin, stdout, stderr = director_connection.exec_command(
        f"kubectl exec -it {pod_name} --namespace={so_namespace} -- bash -c '{config_cmd}'")
    output = stdout.read().decode()
    if "Added `minio` successfully" in output:
        log.info("Added `minio` successfully.")
    else:
        log.error("Minio configuration failed.")
        assert False
    # Run mc ls command for each ManagedElement and pmic
    for managed_element in managed_elements:
        for pmic in pmics:
            enm_name = SO_CENM_CONNECTION_REQUEST["name"]
            minio_path = f"minio/{enm_name}/ericsson/{pmic}/XML/5MIN/ManagedElement={managed_element}/"
            command = f"mc ls {minio_path}"
            log.info(f"Running command: {command}")
            result = \
            director_connection.exec_command(f"kubectl exec -it {pod_name} --namespace={so_namespace} -- {command}")[
                1].read().decode().strip()
            log.info(f"Result for ManagedElement={managed_element} and {pmic}:")
            log.info(result)

def fetch_core_parser_metrics():
    # Get the SO namespace
    so_namespace = SIT.get_so_namespace(SIT)
    # Make the director connection
    try:
        director_connection = get_VMVNFM_host_connection()
    except Exception as e:
        log.error(f"Error connecting to director: {e}")
        return None
    # Get the core parser pod name
    output = director_connection.exec_command(f"kubectl get pods -n {so_namespace} | grep core-parser")[1]
    if not output:
        log.error("Error: No pod found with label 'core-parser'")
        return None
    pod_name = output.read().decode().split()[0]
    # Check if the port is already in use
    port = 8081
    while not port_is_available(port):
        log.info(f"Port {port} is already in use, trying the next port...")
        port += 1
    # Forward the port using screen
    screen_name = f"core_parser_port_{port}"
    port_forward_command = f"screen -dmS {screen_name} bash -c 'kubectl port-forward -n {so_namespace} {pod_name} {port}:8080'"
    director_connection.exec_command(port_forward_command)
    time.sleep(2)
    # Fetch metrics for the core parser service
    metric_values = {}
    for metric in metrics_coreparser:
        curl_command = f"curl http://localhost:{port}/actuator/metrics/{metric}"
        stdin, stdout, stderr = director_connection.exec_command(curl_command)
        result = stdout.read().decode().strip()
        if not result:
            log.error(f"Error: Could not fetch metric {metric}")
            assert False
        value = json.loads(result)['measurements'][0]['value']
        metric_values[metric] = value
        log.info(f"Metric {metric} value: {value}")
    # Stop port forwarding using screen
    stop_port_forward_command = f"screen -S {screen_name} -X quit"
    director_connection.exec_command(stop_port_forward_command)
    time.sleep(2)
    return metric_values

def port_is_available(port):
    # Check if the given port is available
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0