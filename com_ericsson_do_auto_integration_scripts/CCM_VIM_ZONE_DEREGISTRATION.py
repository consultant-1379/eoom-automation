"""
Script to deregister vim zone from cCM.
"""
from com_ericsson_do_auto_integration_utilities.ECM import ECM
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger(__name__)


def deregister_vim_zone():
    """
    Main calling function to deregister vim zone.
    """
    log.info('Inside deregister vim zone function :::')
    ecm = ECM()
    check_and_delete_flavors_if_exist(ecm)
    check_and_delete_images_if_exist(ecm)
    list_and_delete_networks_if_exist(ecm)
    list_and_delete_block_storage_volumes(ecm)
    list_and_delete_vdcs(ecm)
    list_and_delete_security_keys(ecm)
    disconnect_vim_zone(ecm)
    list_and_delete_project(ecm)
    list_and_deregister_vim_zone(ecm)


def check_and_delete_flavors_if_exist(ecm):
    """
    Checks if flavors exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete flavors if exist :::')
    response = ecm.get_flavors().json()
    if 'data' in response and 'srts' in response['data']:
        flavors = response['data']['srts']
        for flavor in flavors:
            delete_response = ecm.delete_flavor(flavor['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def check_and_delete_images_if_exist(ecm):
    """
    Checks if images exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete images if exist :::')
    response = ecm.get_images().json()
    if 'data' in response and 'images' in response['data']:
        images = response['data']['images']
        for image in images:
            delete_response = ecm.delete_image_without_vimzone_copy(image['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def list_and_delete_networks_if_exist(ecm):
    """
    Checks if networks exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete networks if exist :::')
    response = ecm.get_networks().json()
    if 'data' in response and 'vns' in response['data']:
        networks = response['data']['vns']
        for network in networks:
            delete_response = ecm.delete_network(network['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def list_and_delete_block_storage_volumes(ecm):
    """
    Checks if block storage volumes exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete block storage volumes if exist :::')
    response = ecm.get_block_storage_volumes().json()
    if 'data' in response and 'bsvs' in response['data']:
        block_storage_volumes = response['data']['bsvs']
        for block_storage_volume in block_storage_volumes:
            delete_response = ecm.delete_block_storage_volume(block_storage_volume['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def list_and_delete_vdcs(ecm):
    """
    Checks if virtual data centers exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete vdcs if exist :::')
    response = ecm.get_vdcs().json()
    if 'data' in response and 'vdcs' in response['data']:
        vdcs = response['data']['vdcs']
        for vdc in vdcs:
            delete_response = ecm.delete_vdc(vdc['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def list_and_delete_security_keys(ecm):
    """
    Checks if security keys exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete security keys if exist :::')
    response = ecm.get_security_keys().json()
    if 'data' in response and 'securityKeys' in response['data']:
        security_keys = response['data']['securityKeys']
        for security_key in security_keys:
            delete_response = ecm.delete_security_key(security_key['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def disconnect_vim_zone(ecm):
    """
    Disconnects the vim zone.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside disconnect vim zone :::')
    projects_response = ecm.get_projects().json()
    vimzones_response = ecm.get_vimzones().json()
    if 'data' in projects_response and 'projects' in projects_response['data']:
        if 'data' in vimzones_response and 'vimZones' in vimzones_response['data']:
            projects = projects_response['data']['projects']
            vimzone_id = vimzones_response['data']['vimZones'][0]['id']
            for project in projects:
                disconnect_response = ecm.disconnect_vimzone(project['id'], vimzone_id)
                ecm.poll_order_status(disconnect_response.json()['data']['order']['id'])


def list_and_delete_project(ecm):
    """
    Checks if projects exist and deletes them.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside check and delete project if exist :::')
    response = ecm.get_projects().json()
    if 'data' in response and 'projects' in response['data']:
        projects = response['data']['projects']
        for project in projects:
            delete_response = ecm.delete_project(project['id'])
            ecm.poll_order_status(delete_response.json()['data']['order']['id'])


def list_and_deregister_vim_zone(ecm):
    """
    De-registers the vim zone.
    Args:
        ecm (ECM): Ecm object for Ecm API communication
    """
    log.info('Inside final deregister vim zone :::')
    response = ecm.get_vimzones().json()
    if 'data' in response and 'vimZones' in response['data']:
        vimzones = response['data']['vimZones']
        ecm.deregister_vimzone(vimzones[0]['name'])
