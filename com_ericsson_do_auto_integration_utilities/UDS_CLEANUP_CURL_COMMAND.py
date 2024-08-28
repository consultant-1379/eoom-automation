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

class UdsCleanupCurlCommand:
    """
    This class contains all the curl commands for getting the dump of uds resources
    """
    @staticmethod
    def get_service_and_vf_dump(uds_token, uds_hostname):
        curl = (f"curl --insecure -X GET "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/followed")
        return curl

    @staticmethod
    def get_vsp_and_vlm_dump(uds_token, uds_hostname):
        curl = (f"curl --insecure -X GET "
                f"-H 'cookie: JSESSIONID={uds_token}' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Accept: application/json' "
                f"-H 'USER_ID: cs0008' "
                f"https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/items")
        return curl
