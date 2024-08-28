# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2022
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************

from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_model.SIT import SIT
import yaml
import traceback


log = Logger.get_logger('NODESELCTOR_VERIFICATION.py')


def nodeselector_check():
    nested_conn = None
    try:
        log.info('Start getting the pod contents from the namespace')

        namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        nested_conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))
        command = f'kubectl get pods -n {namespace} -o yaml'

        log.info('Executing command: %s', command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        # handle_stderr(stderr, log)
        command_output = stdout.read()
        pod_objects = yaml.load(command_output, Loader=yaml.FullLoader)

        if len(pod_objects['items']) == 0:
            log.error("There were no pods found in the namespace %s to run the nodeSelector test against", namespace)
            assert False

        checks_pods(pod_objects['items'])

    except Exception as e:
        log.error('Error getting the pods from the namespace from ccd director server %s', str(e))
        log.error(traceback.format_exc())
        assert False
    finally:
        nested_conn.close()


def checks_pods(pod_objects_items):
    has_test_failure_occured = None

    for pod_object in pod_objects_items:
        try:
            if check_if_pod_can_be_skipped(str(pod_object['metadata']['name'])):
                log.info("Pod: %s has been marked for being skipped.", str(pod_object['metadata']['name']))
            elif pod_object['spec']['nodeSelector'] == {'kubernetes.io/os': 'linux'}:
                log.info("Pod: %s does have the nodeSelector label", str(pod_object['metadata']['name']))
            else:
                raise Exception("Pod: " + str(pod_object['metadata']['name']) + " does have the nodeSelector label however it is the wrong value. Node Selector label: " + str(pod_object['spec']['nodeSelector']))
        except Exception as e:
            log.error("There was an error fetching the nodeSelector key from Pod: %s", str(pod_object['metadata']['name']))
            log.error(traceback.format_exc())
            has_test_failure_occured = True

    if not has_test_failure_occured:
        assert True
    else:
        assert False


def check_if_pod_can_be_skipped(pod_name):
    skipable_pods=['eric-data-wide-column-database-cd']
    skip_flag = False
    for skipable_pod in skipable_pods:
        if skipable_pod in pod_name:
            skip_flag = True
    return skip_flag
