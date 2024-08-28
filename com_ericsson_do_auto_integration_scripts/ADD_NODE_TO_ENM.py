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
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.SLICE_ASSURANCE_PROPERTIES import managed_elements_objects
from com_ericsson_do_auto_integration_utilities.ENM import ENM
import time

log = Logger.get_logger('ADD_NODE_TO_ENM.py')


def add_nodes_to_ENM():
    enm = ENM()

    # Add nodes to ENM
    log.info("Adding nodes to ENM.")
    for node in managed_elements_objects:
        enm.register_node_in_enm(node["node_name"],
                                 node["node_type"],
                                 node["ossModelIdentity"],
                                 node["ip_address"],
                                 "netsim",
                                 "netsim")

    # PM records appear every 5 min for newly added nodes in ENM
    time.sleep(300)
    pm_files_for_all_nodes_present_in_ENM = True

    # Check for ENM PM records for added nodes
    log.info("Checking for ENM PM records.")
    for node in managed_elements_objects:
        if enm.check_PM_STATISTICAL_5MIN_for_node_in_ENM(node["node_name"]) == False:
            pm_files_for_all_nodes_present_in_ENM = False
            log.info("PM records for node, {}, could not be found in ENM".format(node["node_name"]))
        else:
            log.info("PM records found for node: {}".format(node["node_name"]))

    if pm_files_for_all_nodes_present_in_ENM == True:
        log.info("PM records found for all newly added nodes in ENM")
    else:
        raise RuntimeError("Could not find PM records for all newly added nodes in ENM.")
