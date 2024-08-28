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
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Logger import Logger
import collections

log = Logger.get_logger('ENM.py')

## Note 1: ENM NBI URLS/ENDPOINTS change based on the Node/NE's subnetwork.
##         Not all nodes may belong to a subnetwork

## Note 2: ENM NBI URLS/ENDPOINTS change based on how a node is queried.
## Ex: scopeType=BASE_ALL gets the entire Node/NE MO tree.
##     scopeType=BASE_ONLY gets only the Node/NE's MO.

DO_INIT_FILE = 'do_init.json'

ENM_AUTH = 'https://{0}/login'
ENM_NODE_MANAGEMENT_URL = 'https://{0}/network-visualization/v1/network-elements'
ENM_NBI_URL_WITHOUT_SUBNETWORK = 'https://{0}/enm-nbi/cm/v1/data/{1}?scopeType=BASE_ALL'
ENM_NBI_URL_WITH_SUBNETWORK = 'https://{0}/enm-nbi/cm/v1/data/{1}/{2}?scopeType=BASE_ALL'
ENM_FLS_URL = 'https://{0}/file/v1/files'
ARM_REPOSITORY = 'https://arm.seli.gic.ericsson.se/artifactory/proj-esoa-staging-local-generic-local/esoa-automation'
ENM_NODE_REGISTRATION_TEMPLATE_URL = '{0}/automation-json/enm_node_registration_template.json'.format(ARM_REPOSITORY)
ENM_USERNAME_FIELD_NAME = 'IDToken1'
ENM_PASSWORD_FIELD_NAME = 'IDToken2'


class ENM:

    def __init__(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        self._hostname = sit_data.get_cenm_hostname(sit_data)
        self._username = sit_data.get_cenm_username(sit_data)
        self._password = sit_data.get_cenm_password(sit_data)
        self._node_registration_template = None
        self._session = None

    def set_session(self):
        if self._session is None:
            self._session = requests.Session()
            enm_session_auth_response = self._session.post(ENM_AUTH.format(self._hostname),
                                                           verify=False,
                                                           data={ENM_USERNAME_FIELD_NAME: self._username,
                                                                 ENM_PASSWORD_FIELD_NAME: self._password})
            log.info("ENM Session request http status code: {0}".format(enm_session_auth_response.status_code))
            if enm_session_auth_response.status_code > 299:
                raise RuntimeError("ENM Session could not be created.")

    ## Note: the node registration template already has CM supervision enabled, as well as PM enabled
    def set_node_registration_template(self):
        if self._node_registration_template is None:
            response = requests.get(url=ENM_NODE_REGISTRATION_TEMPLATE_URL,
                                    verify=False,
                                    # The following credentials are stored in Jenkins Credentials Manager (fem1s11-eiffel052)
                                    auth=(os.environ['ESOA_ARM_USERNAME'],
                                          os.environ['ESOA_ARM_PASSWORD']))
            log.info("Get ENM Node Registration Template from ARM status code: {0}".format(response.status_code))
            if response.status_code > 299:
                raise RuntimeError("Could not retrieve ENM node registration template from ESOA arm/artifactory.")
            self._node_registration_template = json.loads(response.text,
                                                          object_pairs_hook=collections.OrderedDict)

    def update_node_registration_template_with(self,
                                               node_name,
                                               node_type,
                                               ossModelIdentity,
                                               node_ip,
                                               node_username,
                                               node_password):

        for obj in self._node_registration_template:
            if obj["type"] == "NetworkElement":
                for attribute in obj["attributes"]:
                    if attribute["key"] == "networkElementName":
                        attribute["value"] = node_name
                    elif attribute["key"] == "ossModelIdentity":
                        attribute["value"] = ossModelIdentity
                    elif attribute["key"] == "neType":
                        attribute["value"] = node_type
            elif obj["type"] == "CbpOiConnectivityInformation":
                for attribute in obj["attributes"]:
                    if attribute["key"] == "ipAddress":
                        attribute["value"] = node_ip
            elif obj["type"] == "NetworkElementSecurity":
                for attribute in obj["attributes"]:
                    if attribute["key"] == "secureUserName":
                        attribute["value"] = node_username
                    elif attribute["key"] == "secureUserPassword":
                        attribute["value"] = node_password

        log.info("Node to be registered in ENM:")
        log.info(json.dumps(self._node_registration_template).replace(" ", ""))

    def register_node_in_enm(self,
                             node_name,
                             node_type,
                             ossModelIdentity,
                             node_ip,
                             node_username,
                             node_password):
        self.set_session()
        self.set_node_registration_template()
        self.update_node_registration_template_with(node_name,
                                                    node_type,
                                                    ossModelIdentity,
                                                    node_ip,
                                                    node_username,
                                                    node_password)
        response = self._session.post(url=ENM_NODE_MANAGEMENT_URL.format(self._hostname),
                                      headers={'Content-Type': 'application/json'},
                                      verify=False,
                                      data=json.dumps(self._node_registration_template).replace(" ", ""))
        log.info("Node registration http response code: {0}".format(response.status_code))
        log.info("Node registration http response reason: {0}".format(response.reason))
        log.info("Node registration http response text: {0}".format(response.text))

        if response.status_code == requests.codes.created:
            log.info("Node, {0} was successfully created.".format(node_name))
        elif response.status_code == 400 and response.text == "ERR_CODE_NE_ALREADY_PRES_IN_DPS":
            log.info("Node already exists in ENM.")
            return
        else:
            raise RuntimeError("Something went wrong. Node could not be created in ENM.")

    # Currently, this function removes the entire Node/NE MO tree from ENM.
    # If you only want to remove the Node/NE from ENM and NOT its decendants,
    # then this function must be rewritten
    def remove_node_from_enm(self,
                             node_name,
                             subnetwork_name=""):

        # Deleting a node from ENM consists of:
        #   - removing the ManagedElement MO (if it exists) AND
        #   - removing the NetworkElement MO

        managed_element = "ManagedElement={0}".format(node_name)
        network_element = "NetworkElement={0}".format(node_name)

        self.set_session()

        if subnetwork_name == "":

            # delete ME MO
            response = self._session.delete(url=ENM_NBI_URL_WITHOUT_SUBNETWORK.format(self._hostname,
                                                                                      managed_element),
                                            verify=False)

            if response.status_code == requests.codes.ok:
                log.info("Successfully deleted ManagedElement for node: {0}".format(managed_element))
            elif response.status_code == requests.codes.not_found:
                log.info("ManagedElement for node, {0}, could not be found".format(node_name))
            else:
                raise RuntimeError("Error deleting ManagedElement for node, {0}, in ENM.".format(node_name))

            # delete NE MO
            response = self._session.delete(url=ENM_NBI_URL_WITHOUT_SUBNETWORK.format(self._hostname,
                                                                                      network_element),
                                            verify=False)

            if response.status_code == requests.codes.ok:
                log.info("Successfully deleted NetworkElement for node: {0}".format(network_element))
            elif response.status_code == requests.codes.not_found:
                log.info("NetworkElement for node, {0}, could not be found".format(node_name))
                log.info("Node, {0}, does not exist in ENM".format(node_name))
                return
            else:
                raise RuntimeError("Error deleting NetworkElement for node, {0}, from ENM.".format(node_name))

            log.info("Node, {0}, has been successfully deleted from ENM".format(node_name))
        else:
            # delete ME MO
            subnetwork = "SubNetwork=" + subnetwork_name
            response = self._session.delete(url=ENM_NBI_URL_WITH_SUBNETWORK.format(self._hostname,
                                                                                   subnetwork,
                                                                                   managed_element,
                                                                                   verify=False))
            if response.status_code == requests.codes.ok:
                log.info("Successfully deleted ManagedElement for node: {0}".format(managed_element))
            elif response.status_code == requests.codes.not_found:
                log.info("ManagedElement for node, {0}, could not be found".format(node_name))
            else:
                raise RuntimeError("Error deleting ManagedElement for node, {0}, in ENM.".format(node_name))

            # delete NE MO
            response = self._session.delete(url=ENM_NBI_URL_WITHOUT_SUBNETWORK.format(self._hostname,
                                                                                      network_element),
                                            verify=False)

            if response.status_code == requests.codes.ok:
                log.info("Successfully deleted NetworkElement for node: {0}".format(network_element))
            elif response.status_code == requests.codes.not_found:
                log.info("NetworkElement for node, {0}, could not be found".format(node_name))
                log.info("Node, {0}, does not exist in ENM".format(node_name))
                return
            else:
                raise RuntimeError("Error deleting NetworkElement for node, {0}, from ENM.".format(node_name))

            log.info("Node, {0}, has been successfully deleted from ENM".format(node_name))

    # checks for PM_STATISTICAL_5MIN records in ENM FLS DB for a specific node
    def check_PM_STATISTICAL_5MIN_for_node_in_ENM(self, node_name):
        self.set_session()

        ENM_filter = "?filter=dataType==PM_STATISTICAL_5MIN;nodeName==*{}&select=id&limit=1&offset=0&orderBy=id%20desc".format(
            node_name)
        latest_PM_ID_URL = ENM_FLS_URL.format(self._hostname) + ENM_filter

        response = self._session.get(url=latest_PM_ID_URL,
                                     headers={'Content-Type': 'application/json'},
                                     verify=False)

        if response.status_code == requests.codes.ok:
            log.info("Successfully fetched latest PM ID for node: {0}".format(node_name))
        else:
            raise RuntimeError("Error while fetching latest PM ID for node, {0}, from ENM.".format(node_name))

        latest_PM_file_ID_raw = json.loads(response.text)

        if len(latest_PM_file_ID_raw["files"]) == 0:
            return False
        else:
            return True