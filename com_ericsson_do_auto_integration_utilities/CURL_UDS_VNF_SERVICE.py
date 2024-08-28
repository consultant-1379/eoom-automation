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
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('CURL_UDS_VNF_SERVICE.py')

class CurlUdsVnfService(object):

    @staticmethod
    def create_vlm_curl(uds_token, uds_hostname):
        """
        Curl command for the creation of VLM
        """
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @createVLM.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models")
        return curl


    @staticmethod
    def get_uds_token_curl(uds_hostname, uds_username, uds_password, tenant):
        """
        Curl command for generation of uds token
        """
        curl = (f"curl "
                f"--insecure "
                f"-X  POST "
                f"-H 'Content-Type: application/json' "
                f"-H 'X-login: {uds_username}' "
                f"-H 'X-password: {uds_password}' "
                f"-H 'X-tenant: {tenant}' "
                f"https://{uds_hostname}/auth/v1/login")
        return curl


    @staticmethod
    def submit_vlm_curl(uds_token, uds_hostname, item_id, version_id):
        """
        Curl command for the submit of VLM
        """
        curl = (f"curl "
                f"--insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @submit.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/"
                f"vendor-license-models/{item_id}/versions/{version_id}/actions")
        return curl

    @staticmethod
    def create_vsp_curl(uds_token, uds_hostname):
        """
        Curl command for the creation of VSP
        """
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @createVSP.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products")
        return curl

    @staticmethod
    def attach_package_curl(uds_token, uds_hostname, item_id, version_id, file_name):
        """
        Curl command for the attachment of package to VSP
        """

        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: multipart/form-data' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' -F 'upload=@{file_name}' "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/"
                f"versions/{version_id}/orchestration-template-candidate")
        return curl

    @staticmethod
    def process_vsp_curl(uds_token, uds_hostname, item_id, version_id):
        """
        Curl command for the process of VSP
        """
        curl = (f"curl --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"--data @test.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/"
                f"versions/{version_id}/orchestration-template-candidate/process")
        return curl

    @staticmethod
    def commit_vsp_curl(uds_token, uds_hostname, item_id, version_id):
        """
        Curl command for the commit of VSP
        """
        curl = (f"curl -i --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @commitVSP.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/items/{item_id}/"
                f"versions/{version_id}/actions")
        return curl

    @staticmethod
    def create_vsp_package_curl(uds_token, uds_hostname, item_id, version_id):
        """
        Curl command for the creation of VSP Package
        """
        curl = (f"curl --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @createPackage.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/"
                f"versions/{version_id}/actions")
        return curl

    @staticmethod
    def create_service_curl(uds_token, uds_hostname, file_name):
        """
        Curl command for the creation of Service
        """
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @{file_name} "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services")
        return curl

    @staticmethod
    def submit_vsp_curl(uds_token, uds_hostname, item_id, version_id):
        """
        Curl command for the submit of VSP
        """
        curl = (f"curl -i --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @submit.json "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/"
                f"versions/{version_id}/actions")
        return curl

    @staticmethod
    def import_vsp_as_vf_curl(uds_token, uds_hostname, MD5_code):
        """
        Curl command for import vsp as vf
        """
        curl = (f"curl --insecure -X POST "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/ "
                f"-H 'Accept: application/json, text/plain, */*' "
                f"-H 'Cache-Control: no-cache' -H 'Connection: keep-alive' "
                f"-H 'Content-MD5: {MD5_code}' -H 'Content-Type: application/json;charset=UTF-8' "
                f"-H 'Cookie: USER_ID=cs0008;JSESSIONID={uds_token}' "
                f"-d @importVSPasVF.json > importvspasVF_result.json")
        return curl

    @staticmethod
    def certify_vf_curl(uds_token, uds_hostname, vsp_as_vf_unique_id):
        """
        Curl command for certify the VF
        """
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' -d @certifyVF.json "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vsp_as_vf_unique_id}/"
                f"lifecycleState/certify")
        return curl

    @staticmethod
    def add_vf_to_service_curl(uds_token, uds_hostname, vnf_service_unique_id):
        """
        Curl command for adding the vf to service
        """
        curl = (f"curl -i --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @addVFtoVNFService.json "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{vnf_service_unique_id}/"
                f"resourceInstance")
        return curl

    @staticmethod
    def certify_service_curl(uds_token, uds_hostname, vnf_service_unique_id):
        """
        Curl command to certify the service
        """
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d @certify.json "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{vnf_service_unique_id}/"
                f"lifecycleState/certify > output_CertifyService.json")
        return curl

    @staticmethod
    def check_connected_systems_curl(uds_token, uds_hostname):
        curl = (f"curl -i --insecure -X GET "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"https://{uds_hostname}/subsystem-manager/v2/subsystems?tenantName=master")
        return curl

    @staticmethod
    def establish_connection(uds_token, uds_hostname, data):
        curl = (f"curl -i --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d '{json.dumps(data)}' "
                f"https://{uds_hostname}/subsystem-manager/v2/subsystems")
        return curl
