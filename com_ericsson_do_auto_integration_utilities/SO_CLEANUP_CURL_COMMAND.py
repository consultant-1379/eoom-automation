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

class SoCleanupCurlCommand:
    """
    This class contains the commands required to abort a held service in SO
    """
    @staticmethod
    def get_held_service_dump(so_token, so_hostname):
        curl = (f"curl --insecure -X GET "
                f"-H 'Accept: application/json' "
                f"-H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={so_token}' "
                f"https://{so_hostname}/serviceOrdering/v4/serviceOrder?offset=0&limit=50&sort=+startDate&state=held"
                )
        return curl

    @staticmethod
    def abort_held_service(so_token, so_hostname, service_id):
        curl = (f"curl --insecure -X POST "
                f"-H 'Accept: application/json' "
                f"-H 'Content-Type: application/json' "
                f"-H 'cookie: JSESSIONID={so_token}' "
                f"https://{so_hostname}/serviceOrdering/v4/serviceOrder/{service_id}/abort"
                )
        return curl
