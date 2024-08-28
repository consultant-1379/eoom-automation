"""
Created on 22-09-2022
contains all the constants and file paths required for UDS VNF and NFV service creation jobs
@author: zbhaper
"""

from com_ericsson_do_auto_integration_model.SIT import SIT

VLM = {"create_vlm_file": "createVLM.json",
       "create_vlm_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createVLM.json",
       "create_vlm_destination_path": f"{SIT.get_base_folder(SIT)}createVLM.json",
       "submit_vlm_file": "submit.json",
       "submit_vlm_source_path": "com_ericsson_do_auto_integration_files/UDS_files/submit.json",
       "submit_vlm_destination_path": f"{SIT.get_base_folder(SIT)}submit.json"
       }
VSP = {"create_vsp_file": "createVSP.json",
       "create_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createVSP.json",
       "create_vsp_destination_path": f"{SIT.get_base_folder(SIT)}createVSP.json",
       "process_vsp_file": "test.json",
       "process_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/test.json",
       "process_vsp_destination_path": f"{SIT.get_base_folder(SIT)}test.json",
       "commit_vsp_file": "commitVSP.json",
       "commit_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/commitVSP.json",
       "commit_vsp_destination_path": f"{SIT.get_base_folder(SIT)}commitVSP.json",
       "submit_vsp_file": "submit.json",
       "submit_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/submit.json",
       "submit_vsp_destination_path": f"{SIT.get_base_folder(SIT)}submit.json",
       "create_vsp_package_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createPackage.json",
       "create_vsp_package_destination_path": f"{SIT.get_base_folder(SIT)}createPackage.json",
       }
VSP_AS_VF = {"import_vsp_file": "importVSPasVF.json",
             "import_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/importVSPasVF.json",
             "import_vsp_destination_path": f"{SIT.get_base_folder(SIT)}importVSPasVF.json",
             "result_source": f"{SIT.get_base_folder(SIT)}importvspasVF_result.json",
             "result_destination": "com_ericsson_do_auto_integration_files/UDS_files/importvspasVF_result.json",
             "certify_vf_file": "certifyVF.json",
             "certify_vf_source_path": "com_ericsson_do_auto_integration_files/UDS_files/certifyVF.json",
             "certify_vf_destination_path": f"{SIT.get_base_folder(SIT)}certifyVF.json"}
NFV_SERVICE = {"nfv_service_file": "createNFVService.json",
               "nfv_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createNFVService.json",
               "nfv_service_destination_path": f"{SIT.get_base_folder(SIT)}createNFVService.json"}
VNF_SERVICE = {"vnf_service_file": "createVNFService.json",
               "vnf_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createVNFService.json",
               "vnf_service_destination_path": f"{SIT.get_base_folder(SIT)}createVNFService.json",
               "add_vnf_service_file": "addVFtoVNFService.json",
               "add_vnf_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/addVFtoVNFService.json",
               "add_vnf_service_destination_path": f"{SIT.get_base_folder(SIT)}addVFtoVNFService.json",
               "certify_vnf_file": "certify.json",
               "certify_vnf_source_path": "com_ericsson_do_auto_integration_files/UDS_files/certify.json",
               "certify_vnf_destination_path": f"{SIT.get_base_folder(SIT)}certify.json",
               "out_certify_destination": "com_ericsson_do_auto_integration_files/UDS_files/output_CertifyService.json",
               "out_certify_source": f"{SIT.get_base_folder(SIT)}output_CertifyService.json",
               "distribute_Service_source": f"{SIT.get_base_folder(SIT)}output_distributeService.txt",
               "distribute_Service_des": "com_ericsson_do_auto_integration_files/UDS_files/output_distributeService.txt"
               }
UDS_ST_CREATION = {"uds_source_path": "com_ericsson_do_auto_integration_files/UDS_files/",
                   "uds_dest_path": SIT.get_base_folder(SIT),
                   "uds_service_file": "uds_service.json",
                   "add_vfc_to_service": "add_vfc_to_service.json",
                   "declare_inputs": "declare_inputs.json",
                   "add_values_to_vfc_inputs": "add_values_to_vfc_inputs.json",
                   "add_values_to_properties": "add_values_to_properties.json",
                   "add_inputs_to_vfc": "add_inputs_to_vfc.json",
                   "add_tosca_function": "add_tosca_function.json",
                   "add_directives": "add_directives.json",
                   "add_node_filter_properties": "add_node_filter_properties.json",
                   "associate_vfc": "associate_vfc.json",
                   "ns_config_template": "nsAdditionalParamTEPG_uds.json",
                   "vnf_config_template": "vnfAdditionalParamTEPG.json",
                   "day1_config_template": "day1ConfigTEPG.xml",
                   "vfc_names": {"geographicSite": "GEOSITE", "vimZone": "VIMZONE0",
                                 "subsystemRef": "SUBSYSTEM", "virtNetworkServ": "NS",
                                 "vnf": "EPG"},
                   "inputs_to_declare": {"GEOSITE": ["name"], "SUBSYSTEM": ["name", "accessId"],
                                         "VIMZONE0": ["name"], "NS": ["name"], "EPG": ["name"]},
                   "input_value_dict": {"GEOSITE": {"name": "Athlone Data Center Test"},
                                        "SUBSYSTEM": {"name": "SOL005_EOCM_367", "accessId": "ECM_Sol005"},
                                        "VIMZONE0": {"name": "vimzone1"},
                                        "NS": {"name": "tepg_sol005"},
                                        "EPG": {"name": "Tosca_EPG_VNFD"}},
                   "inputs_to_add": {"nsdId": "string", "vdcName": "string", "connectionName": "string",
                                     "subnetId": "string", "targetVdc": "string", "vnfmId": "string",
                                     "connectedVn": "string"},
                   "ns_tosca_function_values": {"SO_NS::nsdId": "nsdId", "SO_NS::vdcName": "vdcName",
                                                "CUSTOM_NS::connectedVn": "connectedVn",
                                                "CUSTOM_NS::connectionName": "connectionName",
                                                "CUSTOM_NS::subnetId": "subnetId", "CUSTOM_NS::targetVdc": "targetVdc",
                                                "CUSTOM_NS::vnfmId": "vnfmId"},
                   "ns_properties": {"CUSTOM_NS::connectedVn": "string", "CUSTOM_NS::connectionName": "string",
                                     "CUSTOM_NS::subnetId": "string", "CUSTOM_NS::targetVdc": "string",
                                     "CUSTOM_NS::vnfmId": "string"}
                   }

PACKAGE_NAME = "/Tosca_EPG_VNFD.csar"
TENANT = "master"
fetch_commands = {
    'eo_evnfm_version': f"kubectl get cm eric-installed-applications -n {SIT.get_vm_vnfm_namespace(SIT)} -o yaml | grep -A1 'eric-eo-evnfm' | grep -E 'eric-eo-evnfm' -A1 | paste - - | column -t | awk '{{print $3 \": \" $5}}' | head -1",
    'eo_evnfm_vm_version': f"kubectl get cm eric-installed-applications -n {SIT.get_vm_vnfm_namespace(SIT)} -o yaml | grep -A1 'eric-eo-evnfm-vm' | tail -n1 | awk '{{print $2}}'",
    'eo_cm_version': f"kubectl get cm eric-installed-applications -n {SIT.get_ecm_namespace(SIT)} -o yaml | grep -A1 'eric-eo-cm' | tail -n1 | awk '{{print $2}}'"
}
CONNECTION_REQUEST = {"name": "cCm",
                      "url": "",
                      "vendor": "Ericsson",
                      "subsystemType": {"id": 2,
                                        "type": "NFVO",
                                        "alias": "NFVO"},
                      "adapterLink": "eric-eo-ecmsol005-adapter",
                      "connectionProperties": [{"name": "ECM",
                                                "tenant": "ECM",
                                                "username": "",
                                                "password": "",
                                                "encryptedKeys": ["password"]}
                                               ]
                      }
Pods_check_commands = {
    'get_worker_ips': 'kubectl get nodes -o wide | grep worker | awk \'{print $6}\' > workers',
    'check_not_ready_pods': 'for n in $(cat workers); do ssh $n "sudo crictl pods | grep NotReady ; hostname"; done',
    'delete_not_ready_pods': 'for n in $(cat workers); do ssh $n "sudo crictl rmp \$(sudo crictl pods | awk \'/NotReady/ {print \$1}\')"; done'
}
UDS_NFV_SERVICE_PROPERTIES = [
    {
        "propertyConstraints": None,
        "defaultValue": None,
        "description": "Identifier of the NS Deployment Flavour within the NSD",
        "name": "flavour_id",
        "parentUniqueId": "",
        "password": False,
        "required": True,
        "schema": {
            "property": {

            }
        },
        "schemaType": None,
        "type": "string",
        "uniqueId": "",
        "value": "default",
        "definition": False,
        "getInputValues": None,
        "parentPropertyType": None,
        "subPropertyInputPath": None,
        "toscaPresentation": {
            "ownerId": ""
        },
        "getPolicyValues": None,
        "inputPath": None,
        "metadata": None,
        "subPropertyToscaFunctions": None
    }
]

so_token_user = "so-user"
so_token_password = "Ericsson123!"
so_token_tenant = "master"
so_token_url = "https://{0}/auth/v1/login"
so_connection_url = "https://{}/subsystem-manager/v2/subsystems"

SO_CENM_CONNECTION_REQUEST = {"name": "enm-flexi7123",
                      "url": "",
                      "vendor": "Ericsson",
                      "subsystemType": {"id": 2,
                                        "type": "DomainManager",
                                        "alias": "DomainManager"},
                      "adapterLink": "eric-eo-enm-adapter",
                      "connectionProperties": [{"username":"","password":"","name":"enm-flexi7123","scriptingVMs":"10.65.10.17","sftpPort":"22","encryptedKeys":["password"]}]
                      }

managed_elements = ["5G132PCC001", "5G132PCC002"]
pmics = ["pmic1", "pmic2"]

metrics_sftp = [
    "num_input_kafka_messages_received_total",
    "num_output_kafka_messages_produced_successfully",
    "num_successful_bdr_uploads_total",
    "num_successful_file_transfer_total",
    "num_failed_bdr_uploads_total",
    "num_failed_file_transfer_total",
    "num_output_kafka_messages_failed_total",
    "processed_bdr_data_volume_total",
    "processed_counter_file_data_volume_total",
    "processed_counter_files_time_total"
]
zero_threshold = {
    "num_input_kafka_messages_received_total": 0,
    "num_output_kafka_messages_produced_successfully": 0,
    "num_successful_bdr_uploads_total": 0,
    "num_successful_file_transfer_total": 0,
    "processed_bdr_data_volume_total": 0,
    "processed_counter_file_data_volume_total": 0,
    "processed_counter_files_time_total": 0
}

greater_than_zero_threshold = {
    "num_failed_bdr_uploads_total": 0,
    "num_failed_file_transfer_total": 0,
    "num_output_kafka_messages_failed_total": 0
}

metrics_coreparser = [
    "eric.oss.3gpp.parser.pm.xml.core.num.successful.metrics.parsed",
    "eric.oss.3gpp.parser.pm.xml.core.num.input.kafka.messages.received.total",
    "eric.oss.3gpp.parser.pm.xml.core.num.output.kafka.messages.failed.total",
    "eric.oss.3gpp.parser.pm.xml.core.num.output.kafka.messages.produced.successfully",
    "eric.oss.3gpp.parser.pm.xml.core.num.successful.bdr.downloads.total",
    "eric.oss.3gpp.parser.pm.xml.core.num.failed.bdr.downloads.total"
]