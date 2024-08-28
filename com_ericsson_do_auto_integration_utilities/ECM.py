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
import base64
import requests
import urllib3

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Requests_utilities import rest_retry
from http import HTTPStatus

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = Logger.get_logger(__name__)
DO_INIT_FILE = 'do_init.json'

VM_VNFM_DIRECTOR_SERVER_PEM = 'eccd-2-3.pem'
ECM_TOKENS = 'https://{0}:443/ecm_service/tokens'
ECM_VNF_PACKAGES = 'https://{0}/ecm_service/vnfpackages'
ECM_NS_DESCRIPTORS = 'https://{0}/ecm_service/SOL005/nsd/v1/ns_descriptors'
ECM_VNFPKGM_VNF_PACKAGES = 'https://{0}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages'
ECM_CISM_CLUSTERS = 'https://{0}/ecm_service/cisms'
ECM_ORDER_STATUS = 'https://{0}/ecm_service/v2/orders/{1}'

ECM_DELETE_FLAVOR = 'https://{0}/ecm_service/srts/{1}'
ECM_DELETE_IMAGE_WITHOUT_VIMZONE_COPY_QUERY = \
    'https://{0}/ecm_service/images/{1}?%24data=%7B%22deleteVimCopies%22%3Afalse%7D'
ECM_DELETE_NETWORK = 'https://{0}/ecm_service/v2/vns/{1}'
ECM_DELETE_BSV = 'https://{0}/ecm_service/bsvs/{1}'
ECM_DELETE_VDC = 'https://{0}/ecm_service/vdcs/{1}'
ECM_DELETE_SECURITY_KEY = 'https://{0}/ecm_service/securitykeys/{1}'
ECM_DELETE_PROJECT = 'https://{0}/ecm_service/projects/{1}'
ECM_DELETE_VIMZONE = 'https://{0}/ecm_service/vimzones/{1}'
ECM_DISCONNECT_VIM_ZONE = 'https://{0}/ecm_service/projects/{1}/delete'

ECM_FLAVORS = 'https://{0}/ecm_service/srts'
ECM_IMAGES = 'https://{0}/ecm_service/images'
ECM_NETWORKS = 'https://{0}/ecm_service/v2/vns'
ECM_BLOCK_STORAGE_VOLUMES = 'https://{0}/ecm_service/bsvs'
ECM_VDCS = 'https://{0}/ecm_service/vdcs'
ECM_SECURITY_KEYS = 'https://{0}/ecm_service/securitykeys'
ECM_PROJECTS = 'https://{0}/ecm_service/projects'
ECM_VIM_ZONES = 'https://{0}/ecm_service/vimzones'


class ECM:
    def __init__(self):
        with open(DO_INIT_FILE, 'r') as init_file:
            data = json.load(init_file)
        self._hostname = data['CORE_VM_Hostname']
        self._username = data['ECM_GUI_Username']
        self._password = data['ECM_GUI_Password']
        self._tenant = data['TENANT_NAME']
        self._token = None
        self._environment = data['ENVIRONMENT']
        self._headers = {'Content-Type': 'application/json', 'AuthToken': '{0}'.format(self.get_token())}
        self._cism_register_url = data['CISM_REGISTER_URL']
        self._director_server_ip = data['VM_VNFM_DIRECTOR_IP']
        self._director_server_username = data['VM_VNFM_DIRECTOR_USERNAME']
        if data.get('VM_VNFM_DIRECTOR_PEM'):
            self._director_server_pemkey = data['VM_VNFM_DIRECTOR_PEM']
        else:
            self._director_server_pemkey = VM_VNFM_DIRECTOR_SERVER_PEM

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        self._hostname = value

    def get_token(self):
        if self._token is None:
            auth_basic = base64.b64encode(bytes(self._username + ':' + self._password, encoding='utf-8'))
            decoded_auth_basic = auth_basic.decode('utf-8')
            response = requests.post(url=ECM_TOKENS.format(self._hostname),
                                     headers={'Authorization': 'Basic {}'.format(decoded_auth_basic),
                                              'TenantId': self._tenant},
                                     verify=False).json()
            self._token = response['status']['credentials']
        return self._token

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved flavors', on_fail='Failed to retrieve flavors')
    def get_flavors(self):
        """
        Retrieve flavors from the ECM instance.
        Returns:
            requests.Response: The response object including the data with flavors.
        """
        return requests.get(url=ECM_FLAVORS.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted flavor', on_fail='Failed to delete flavor')
    def delete_flavor(self, flavor_id):
        """
        Delete a flavor from the ECM instance.
        Args:
            flavor_id (str): Query parameter specifying the id of the flavor to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the flavor deletion.
        """
        return requests.delete(url=ECM_DELETE_FLAVOR.format(self._hostname, flavor_id), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved images', on_fail='Failed to retrieve images')
    def get_images(self):
        """
        Retrieve images from the ECM instance.
        Returns:
            requests.Response: The response object including the data with images.
        """
        return requests.get(url=ECM_IMAGES.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted image', on_fail='Failed to delete image')
    def delete_image_without_vimzone_copy(self, image_id):
        """
        Delete an image from the ECM instance.
        Args:
            image_id (str): Query parameter specifying the id of the image to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the image deletion.
        """
        return requests.delete(url=ECM_DELETE_IMAGE_WITHOUT_VIMZONE_COPY_QUERY.format(self._hostname, image_id),
                               headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved networks', on_fail='Failed to retrieve networks')
    def get_networks(self):
        """
        Retrieve networks from the ECM instance.
        Returns:
            requests.Response: The response object including the data with networks.
        """
        return requests.get(url=ECM_NETWORKS.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted network', on_fail='Failed to delete network')
    def delete_network(self, network_id):
        """
        Delete a network from the ECM instance.
        Args:
            network_id (str): Query parameter specifying the id of the network to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the network deletion.
        """
        return requests.delete(url=ECM_DELETE_NETWORK.format(self._hostname, network_id), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved block storage volumes',
                on_fail='Failed to retrieve block storage volumes')
    def get_block_storage_volumes(self):
        """
        Retrieve block storage volumes from the ECM instance.
        Returns:
            requests.Response: The response object including the data with block storage volumes.
        """
        return requests.get(url=ECM_BLOCK_STORAGE_VOLUMES.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted block storage volume', on_fail='Failed to delete block storage volume')
    def delete_block_storage_volume(self, bsv_id):
        """
        Delete a block storage volume from the ECM instance.
        Args:
            bsv_id (str): Query parameter specifying the id of the block storage volume to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the block storage volume
            deletion.
        """
        return requests.delete(url=ECM_DELETE_BSV.format(self._hostname, bsv_id), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved vdcs', on_fail='Failed to retrieve vdcs')
    def get_vdcs(self):
        """
        Retrieve vdcs from the ECM instance.
        Returns:
            requests.Response: The response object including the data with vdcs.
        """
        return requests.get(url=ECM_VDCS.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted vdc', on_fail='Failed to delete vdc')
    def delete_vdc(self, vdc_id):
        """
        Delete a vdc from the ECM instance.
        Args:
            vdc_id (str): Query parameter specifying the id of the vdc to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the vdc deletion.
        """
        return requests.delete(url=ECM_DELETE_VDC.format(self._hostname, vdc_id), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved security keys', on_fail='Failed to retrieve security keys')
    def get_security_keys(self):
        """
        Retrieve security keys from the ECM instance.
        Returns:
            requests.Response: The response object including the data with security keys.
        """
        return requests.get(url=ECM_SECURITY_KEYS.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted security key', on_fail='Failed to delete security key')
    def delete_security_key(self, security_key_id):
        """
        Delete a security key from the ECM instance.
        Args:
            security_key_id (str): Query parameter specifying the id of the security key to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the security key deletion.
        """
        return requests.delete(url=ECM_DELETE_SECURITY_KEY.format(self._hostname, security_key_id),
                               headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully disconnected vimzone', on_fail='Failed to disconnect vimzone')
    def disconnect_vimzone(self, project_id, vimzone_id):
        """
        Disconnect vimzone from the ECM instance.
        Args:
            project_id (str): Query parameter specifying the id of the project to disconnect the vimzone from.
            vimzone_id (str): Query parameter specifying the id of the vimzone to be disconnected.
        Returns:
            requests.Response: The response object indicating the success or failure of the vimzone disconnection.
        """
        return requests.post(url=ECM_DISCONNECT_VIM_ZONE.format(self._hostname, project_id),
                             headers=self._headers, verify=False,
                             json={'vimZoneConnections': [{'vimZoneId': vimzone_id}]})

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved projects', on_fail='Failed to retrieve projects')
    def get_projects(self):
        """
        Retrieve projects from the ECM instance.
        Returns:
            requests.Response: The response object including the data with projects.
        """
        return requests.get(url=ECM_PROJECTS.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deleted project', on_fail='Failed to delete project')
    def delete_project(self, project_id):
        """
        Delete a project from the ECM instance.
        Args:
            project_id (str): Query parameter specifying the id of the project to be deleted.
        Returns:
            requests.Response: The response object indicating the success or failure of the project deletion.
        """
        return requests.delete(url=ECM_DELETE_PROJECT.format(self._hostname, project_id), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully retrieved vimzones', on_fail='Failed to retrieve vimzones')
    def get_vimzones(self):
        """
        Retrieve vimzones from the ECM instance.
        Returns:
            requests.Response: The response object including the data with vimzones.
        """
        return requests.get(url=ECM_VIM_ZONES.format(self._hostname), headers=self._headers, verify=False)

    @rest_retry(max_retries=1, wait_time=0, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('status').get('reqStatus'), expected_data='SUCCESS',
                on_success='Successfully deregistered vimzone', on_fail='Failed to deregister vimzone')
    def deregister_vimzone(self, vimzone_name):
        """
        Deregister a vimzone from the ECM instance.
        Args:
            vimzone_name (str): Query parameter specifying the name of the vimzone to be deregistered.
        Returns:
            requests.Response: The response object indicating the success or failure of the vimzone deregisteration.
        """
        return requests.delete(url=ECM_DELETE_VIMZONE.format(self._hostname, vimzone_name), headers=self._headers,
                               verify=False)

    @rest_retry(max_retries=9, wait_time=10, allowed_codes=(HTTPStatus.OK,), logger=log,
                response_filter=lambda response: response.get('data').get('order').get('orderReqStatus'),
                expected_data=['COM', 'WARN'], failure_data=['ERR'], on_success='Order status is completed',
                on_fail='Order status is failed', is_order_poll=True)
    def poll_order_status(self, order_id):
        """
        Poll order status from the ECM instance.
        Args:
            order_id (str): The id of the order to be polled.
        Returns:
            requests.Response: The response object of polling the order.
        """
        return requests.get(ECM_ORDER_STATUS.format(self._hostname, order_id), headers=self._headers, verify=False)
