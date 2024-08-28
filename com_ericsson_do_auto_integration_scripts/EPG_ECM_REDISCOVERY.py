from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger

from com_ericsson_do_auto_integration_scripts.ECM_NODE_REDISCOVERY import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *



log = Logger.get_logger('EPG_ECM_REDISCOVERY.py')

def epg_discovery_workflow_deployment():
    discovery_workflow_deployment('EPG')


def delete_epg_vapp_entry_cmdb():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    global epg_vapp_name
    epg_vapp_name = sit_data._SIT__epg_vapp_name
    global vdcname
    #vdcname = sit_data._SIT__vdc_name
    global vdc_id
    #vdc_id = sit_data._SIT__vdc_id
    
    vdcname,vdc_id = fetch_vdc_name_id_EOCM(epg_vapp_name,'EPG')

    delete_vapp_entry_cmdb(epg_vapp_name,vdcname)

def delete_epg_vapp_vnflcmdb():
    delete_vapp_vnflcmdb(epg_vapp_name)


def epg_list_discovery():
    list_discovery(epg_vapp_name)

def epg_discover_vapp():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

    vnfm_id = sit_data._SIT__vnfManagers
    vnf_packageid = sit_data._SIT__vnf_packageId
    vimzone_name = sit_data._SIT__vimzone_name
    #while deleting Service / vapp as part of pipeline getting error sometimes that the vdc is in use already and cant delete the service,so thats why replacing the vdc_id to default_vdc_id
    default_vdc_id = sit_data._SIT__vdc_id
    discover_vapp(epg_vapp_name, vnfm_id, epg_vapp_name, default_vdc_id, vnf_packageid, vimzone_name)


def epg_discover_workflow_status():
    node_defination_name = 'Discover VNF v1'
    check_lcm_workflow_status(epg_vapp_name,node_defination_name)
