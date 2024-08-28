
from com_ericsson_do_auto_integration_scripts.WORKFLOW_INSTALLATION import ecm_server_ip, ecm_username, ecm_password
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger

from com_ericsson_do_auto_integration_model.SIT import SIT
import re

log = Logger.get_logger('STOP_NETSIM.py')

def execute_command(connection, command, ne_names=False, use_tail=False):
    command = f'echo -e "{command}" | /netsim/inst/netsim_pipe'
    if ne_names:
        command += " | grep -oP '^\S+' | grep -v '^\(NE\|OK\)$'"
    if use_tail:
        command += " | tail -1"
    stdin, stdout, stderr = connection.exec_command(command)
    error = stderr.read().decode().strip()
    output = stdout.read().decode().strip()
    if error:
        log.error("Error encountered while running command: %s", command)
        log.error(error)
    else:
        log.info("Command executed successfully: %s", command)

    if len(output.split('\n')) == 1:
        return output.split('\n')[0]
    else:
        return output.split('\n')[1:]

def extract_simnes(output):
    simnes_list = []
    for line in output:
        match = re.search(r'\b(\w+)\s+LTE', line)
        if match:
            simnes_list.append(match.group(1))
    return simnes_list

def stop_node_if_started():

    # Connect to destination server
    nested_conn = ServerConnection.make_nested_server_connection(
        ecm_server_ip,
        ecm_username,
        ecm_password,
        SIT.get_netsim_ip(SIT),
        SIT.get_netsim_username(SIT),
        SIT.get_netsim_password(SIT)
    )

    # Verify the connection
    if nested_conn is not None:
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
                log.info("Processing simnes_value: %s", simnes_value)

                # Ignore the '>>' prefix from simnes value
                simnes_value = simnes_value.replace('>>', '').strip()

                # Execute the '.isstarted' command to check the node's state
                is_started_command = f'{open_simulation_command} \\n .select {simnes_value} \\n .isstarted'
                is_started_output = execute_command(nested_conn, is_started_command, ne_names=False, use_tail=True)
                log.info("Command: %s", is_started_command)
                log.info("Output:\n%s", is_started_output)

                # Check if the output is "Started"
                if "Started" in is_started_output:
                    log.info("Node is in 'Started' state")
                    # Execute the '.stop' command to stop the node
                    stop_command = f'{open_simulation_command} \\n .select {simnes_value} \\n .stop'
                    stop_output = execute_command(nested_conn, stop_command, ne_names=False, use_tail=True)
                    log.info("Stop Command: %s", stop_command)
                    log.info("Stop Output: %s", stop_output)
                else:
                    log.info("Node is already in 'Not Started' state")

        log.info("stop_node_if_started function completed")

    return nested_conn


