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


class UdsDeleteCurlCommand:
    """
    This class contains all the curl commands for deleting the uds pre req
    """
    @staticmethod
    def archive_vlm_curl(uds_token, uds_hostname, data, vlm_id):
        curl = (f"curl --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d '{json.dumps(data)}' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"onboarding-api/v1.0/items/{vlm_id}/actions")
        return curl

    @staticmethod
    def archive_vsp_curl(uds_token, uds_hostname, data, vfc_id):
        curl = (f"curl --insecure -X PUT "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d '{json.dumps(data)}' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"onboarding-api/v1.0/items/{vfc_id}/actions")
        return curl

    @staticmethod
    def archive_vfc_curl(uds_token, uds_hostname, data, vfc_id):
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d {data} "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"rest/v1/catalog/resources/{vfc_id}/archive")
        return curl

    @staticmethod
    def archive_service_curl(uds_token, uds_hostname, data, service_id):
        curl = (f"curl --insecure -X POST "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d {data} "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/"
                f"services/{service_id}/archive")
        return curl

    @staticmethod
    def delete_vlm_curl(uds_token, uds_hostname, data, vlm_id):
        curl = (f"curl --insecure -X DELETE "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d '{data}' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"onboarding-api/v1.0/vendor-license-models//{vlm_id}")
        return curl

    @staticmethod
    def delete_vsp_curl(uds_token, uds_hostname, data, vfc_id):
        curl = (f"curl --insecure -X DELETE "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"-d '{data}' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"onboarding-api/v1.0/vendor-software-products//{vfc_id}")
        return curl

    @staticmethod
    def delete_vfc_curl(uds_token, uds_hostname, vfc_id):
        curl = (f"curl --insecure -X DELETE "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"rest/v1/catalog/resources/{vfc_id}?deleteAction=DELETE")
        return curl

    @staticmethod
    def delete_service_curl(uds_token, uds_hostname, service_id):
        curl = (f"curl --insecure -X DELETE "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"https://{uds_hostname}/sdc1/feProxy/"
                f"rest/v1/catalog/services/{service_id}?deleteAction=DELETE")
        return curl
