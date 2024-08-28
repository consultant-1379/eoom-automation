from behave import *
from com_ericsson_do_auto_integration_scripts.SO_CNF_CONFIGMAP_DEPL import CnfconfigmapDepl as so_cnf_depl


@step("I start the ESOA Scenario to create NSD package")
def step_impl(context):
     so_cnf_depl.create_cnfns_nsd_package(so_cnf_depl)
    
@step("I start the ESOA Scenario to Upload etsi toscs nsd packages")
def step_impl(context):
    so_cnf_depl.upload_etsi_tosca_nsd_pkg(so_cnf_depl)


@step("I start the ESOA Scenario to onboard cnf config-map config templates on so")
def step_impl(context):
    so_cnf_depl.upload_cnf_configmap_config_templates(so_cnf_depl, is_esoa=True)


@step("I start the ESOA Scenario to create the subsystem on SO")
def step_impl(context):
    so_cnf_depl.onboard_sol_cnf_subsytems(so_cnf_depl)


@step("I start the ESOA Scenario to upload sol cnf service templates")
def step_impl(context):
    so_cnf_depl.onboard_sol_bgf_service_template(so_cnf_depl, is_esoa=True)


@step("I start the ESOA Scenario to deploy the sol cnf netwrok service")
def step_impl(context):
    so_cnf_depl.create_sol_cnf_network_service(so_cnf_depl, is_esoa=True)

@step("I start the ESOA Scenario to verify the sol cnf network service")
def step_impl(context):
    so_cnf_depl.verify_cnf_so_network_service(so_cnf_depl, is_esoa=True)
