import requests
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def list_objects_from_splose(base_url: str, this_url: str, secret: str, accumulated_object_list = [], params = None) -> requests.Response:
    """
    Query data from the Splose API endpoint.
    """
    header_with_bearer_token_auth = {
        'Authorization': 'Bearer ' + secret,
        'Content-Type': 'application/json'
    }
    logging.info(f"Querying Splose API endpoint: {base_url}{this_url} with params: {params}")
    response = requests.get(f"{base_url}{this_url}", headers=header_with_bearer_token_auth, params=params)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(response.json())
    # get the list of objects from the response
    object_list = response.json().get('data', [])
    # check if there is a next page link in the response
    next_page_links = response.json().get('links', {})
    logging.info(f"Number of objects retrieved: {len(object_list)}")
    accumulated_object_list.extend(object_list)
    # if next_page_links['nextPage'] is empty or does not exist, return response
    if not next_page_links.get('nextPage') or not next_page_links.get('nextPage').startswith(this_url[:3]):
        return accumulated_object_list
    else:
        return list_objects_from_splose(base_url, next_page_links['nextPage'], secret, accumulated_object_list)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def get_one_object_from_splose(base_url: str, this_url: str, secret, object_id) -> requests.Response:
    """
    Query data from the Splose API endpoint for a single object.
    """
    header_with_bearer_token_auth = {
        'Authorization': 'Bearer ' + secret,
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{base_url}{this_url}/{object_id}", headers=header_with_bearer_token_auth)
    return response

