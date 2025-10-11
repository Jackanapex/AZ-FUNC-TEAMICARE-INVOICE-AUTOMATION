import requests
from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

def double(value: int) -> int:
    return value * 2

class AlayaCareDataQuery:
    def __init__(self, username: str, password: str, url: str, params: dict) -> None:
        self.username = username
        self.password = password
        self.url = url
        self.query_params = params
        self.query_header = {
            'Accept': 'application/json'
        }
        self.basic_auth_object = requests.auth.HTTPBasicAuth(self.username, self.password)

    def _set_basic_auth(self, username: str, password: str) -> None:
        """
        Set the basic authentication header using the provided username and password.
        """
        if username and password:
            self.username = username
            self.password = password
        self.basic_auth_object = requests.auth.HTTPBasicAuth(self.username, self.password)

    def _set_params(self, params: dict) -> None:
        """
        Set the query parameters for the API request.
        """
        if type(params) is dict and len(params) > 0:
            self.query_params = params
    
    def _append_params(self, additional_params: dict) -> None:
        """
        Append additional parameters to the existing query parameters.
        """
        if type(additional_params) is dict and len(additional_params) > 0:
            self.query_params.update(additional_params)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(5),
        retry=retry_if_exception_type(Exception)
    )
    def query_data_from_endpoint(self) -> requests.Response:
        """
        Query data from the AlayaCare API endpoint.
        """
        response = requests.get(self.url, headers=self.query_header, params=self.query_params, auth=self.basic_auth_object)
        return response

class AlayaCareDataQueryBillableItem(AlayaCareDataQuery):
    def __init__(self, username: str, password: str, url: str, params: dict) -> None:
        """
        Initialize the AlayaCareDataQueryBillableItem with specific parameters.
        """
        validate_params = params.copy()
        if ('start_date' not in validate_params) and ('end_date' not in validate_params):
            validate_params.update({'start_date': (dt.now(tz.utc) + timedelta(days=-30)).strftime('%Y-%m-%dT%H:%M:%SZ')})
            validate_params.update({'end_date': dt.now(tz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
        super().__init__(username, password, url, validate_params)
        
    def get_total_billable_item_count(self) -> int:
        """
        Get the total count of billable item from the API response.
        """
        self._append_params({'count': 1})
        response = self.query_data_from_endpoint()
        if response.status_code == 200:
            data = response.json()
            return data.get('total_items', 0)
        else:
            raise Exception(response.json())

    def get_list_of_billable_items(self, count: int = 5000, page: int = 1) -> list:
        """
        Get the list of billable items from the API response.
        """
        self._append_params({'count': count, 'page': page})
        response = self.query_data_from_endpoint()
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            raise Exception(response.json())
    
    def calculate_pagination(self, total_items: int, count: int) -> int:
        """
        Calculate the number of pages needed based on total items and count per page.
        """
        if total_items <= 0 or count <= 0:
            return 0
        return (total_items + count - 1) // count
