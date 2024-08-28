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
from com_ericsson_do_auto_integration_utilities.ENM import ENM
from com_ericsson_do_auto_integration_utilities.SLICE_ASSURANCE_PROPERTIES import managed_elements_objects

log = Logger.get_logger('DELETE_NODE_FROM_ENM.py')

def delete_nodes_from_ENM():
    enm = ENM()

    log.info("Deleting nodes from ENM.")
    for node in managed_elements_objects:
        enm.remove_node_from_enm(node["node_name"], "")