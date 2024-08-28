import time
import requests
from functools import wraps
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger(__name__)


def rest_retry(max_retries=3, wait_time=60, allowed_codes=(500,), logger=None, response_filter=None,
               expected_data=None, failure_data=None, on_success="", on_fail="", is_order_poll=False):
    """
    Decorator to retry a function call if the response code is in the allowed_codes list
    :param max_retries: Maximum number of retries
    :param wait_time: Time to wait between retries
    :param allowed_codes: List of allowed response codes
    :param logger: Logger object
    :param response_filter: Function to filter the response
    :param expected_data: Expected data in the response
    :param failure_data: Expected failure data in the response
    :param on_success: Message to log on success
    :param on_fail: Message to log on failure
    :param is_order_poll: Boolean value to indicate if the request is for order polling
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(func.__name__ + ' is called.')
            retries = 0
            while retries < max_retries:
                try:
                    response = func(*args, **kwargs)
                    if response.status_code in allowed_codes:
                        logger.info(f"Request succeeded with status code {response.status_code}")
                        filtered_result = None
                        if response_filter is not None:
                            filtered_result = response_filter(response.json())
                        if expected_data is not None and filtered_result is not None:
                            if filtered_result in expected_data:
                                logger.info(f'{on_success} ::: {response.json()}')
                                return response
                            elif failure_data is not None and filtered_result in failure_data:
                                logger.info(f'{on_fail} ::: {response.json()}')
                                assert False
                            elif not is_order_poll:
                                logger.info(f"Response data received ::: {response.json()}")
                                logger.error(on_fail)
                                raise Exception(on_fail)
                    else:
                        logger.warning(
                            f"Received response code {response.status_code}, response data {response.json()}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request error: {str(e)}")
                logger.info(f"Sleeping for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                retries += 1
            logger.error(f"Max retries exceeded")
            assert False

        return wrapper

    if logger is None:
        logger = Logger.get_logger(__name__)

    return decorator
