
from com_ericsson_do_auto_integration_scripts.WORKFLOW_INSTALLATION import ecm_server_ip, ecm_username, ecm_password
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
import re
import os

log = Logger.get_logger('Start_netsim.py')

def execute_command(connection, ns_command, ne_names=False, use_tail=False):
    ns_command = f'echo -e "{ns_command}" | /netsim/inst/netsim_pipe'
    if ne_names:
        ns_command += " | grep -oP '^\S+' | grep -v '^\(NE\|OK\)$'"
    if use_tail:
        ns_command += " | tail -1"
    stdin, stdout, stderr = connection.exec_command(ns_command)
    error = stderr.read().decode().strip()
    output = stdout.read().decode().strip()
    if error:
        log.error("Error encountered while running command: %s", ns_command)
        log.error(error)
    else:
        log.info("Command executed successfully: %s", ns_command)

    if len(output.split('\n')) == 1:
        return output.split('\n')[0]
    else:
        return output.split('\n')[1:]


def extract_simnes(simnes_output):
    simnes_list = []
    for line in simnes_output:
        match = re.search(r'\b(\w+)\s+LTE', line)
        if match:
            simnes_list.append(match.group(1))
    return simnes_list


def connect_to_netsim_server():
    """
        Connects to the destination server and performs operations on NetSim server.
        NETSIM Details are being taken from the JENKINS
        """
    nested_conn = ServerConnection.make_nested_server_connection(
        ecm_server_ip,
        ecm_username,
        ecm_password,
        os.environ['NETSIM_IP_ADDRESS'],
        os.environ['NETSIM_USERNAME'],
        os.environ['NETSIM_PASSWORD']
    )

    # Verify the connection
    if nested_conn:
        log.info("Connection to NetSim server established successfully.")

        # Execute '.show simulations' command
        show_simulations_command = ".show simulations"
        show_simulations_output = execute_command(nested_conn, show_simulations_command)
        log.info("Command: %s", show_simulations_command)
        log.info("Output:\n%s", show_simulations_output)

        # Ignore 'default' simulation
        simulations = [sim for sim in show_simulations_output if sim != 'default']

        # Iterate over simulations
        for simulation in simulations:
            # Execute '.open' command for each simulation
            open_simulation_command = f".open {simulation}"
            open_simulation_output = execute_command(nested_conn, open_simulation_command)
            log.info("Command: %s", open_simulation_command)
            log.info("Output: %s", open_simulation_output)

            # Execute '.show simnes' command and get simnes_values
            show_simnes_command = ".show simnes"
            echo_command = f'{open_simulation_command} \\n{show_simnes_command}'
            show_simnes_output = execute_command(nested_conn, echo_command, ne_names=True, use_tail=False)
            log.info("Command: %s", echo_command)
            log.info("Output:\n%s", show_simnes_output)

            for simnes_value in show_simnes_output:
                # Ignore the '>>' prefix from simnes value
                simnes_value = simnes_value.replace('>>', '').strip()
                # Execute the desired command
                desired_command = f'{open_simulation_command} \\n .select {simnes_value} \\n .isstarted'
                desired_output = execute_command(nested_conn, desired_command, ne_names=False, use_tail=True)
                log.info("Command: %s", desired_command)
                log.info("Output:\n%s", desired_output)

                # Check if the output is "NotStarted"
                if "NotStarted" in desired_output:
                    # Execute the start command
                    start_command = f'{open_simulation_command} \\n .select {simnes_value} \\n .start'
                    start_output = execute_command(nested_conn, start_command, ne_names=False, use_tail=True)
                    log.info("Start Command: %s", start_command)
                    log.info("Start Output: %s", start_output)
                else:
                    log.info("Node is already in 'Started' state")

        log.info("connect_to_netsim_server function completed")

    else:
        log.error("Failed to establish connection to NetSim server.")
        assert False



