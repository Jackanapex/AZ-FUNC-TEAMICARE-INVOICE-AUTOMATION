import requests
import json

class TechoneDataQuery:
    def __init__(self, auth_token: str, page_size: int = 50000, page: int = 1):
        """
        Base class for Techone data queries with authentication and pagination.

        :param auth_token: The authentication token for the query.
        :param page_size: The number of items per page (default is 50000).
        :param page: The page number to query (default is 1).
        """
        self.auth_token = auth_token
        self.query_header = {
            'Authorization': 'Basic ' + self.auth_token,
        }
        self.params = {
            'pageSize': page_size,
            'page': page
        }

    def set_page_size(self, new_page_size: int) -> str:
        """
        Update the pageSize value in the params dictionary.

        :param new_page_size: The new page size value to set.
        """
        self.params['pageSize'] = new_page_size
        return f"Page size updated to: {new_page_size}"

    def set_page(self, target_page: int) -> str:
        """
        Update the page value in the params dictionary.

        :param target_page: The new page number to set.
        """
        self.params['page'] = target_page
        return f"Page updated to: {target_page}"

    def get_query_info(self) -> str:
        """
        Returns a string with the authentication token and query parameters.
        """
        return f"Auth Token: {self.auth_token}, Query Parameters: {self.params}"

class TechoneDataQueryWithCustomParams(TechoneDataQuery):
    def __init__(self, auth_token: str, page_size: int = 50000, page: int = 1, custom_params: dict = None):
        """
        Subclass for queries with custom parameters.

        :param auth_token: The authentication token for the query.
        :param page_size: The number of items per page (default is 50000).
        :param page: The page number to query (default is 1).
        :param custom_params: A dictionary of custom parameters for the query.
        """
        super().__init__(auth_token, page_size, page)
        if custom_params:
            self.params.update(custom_params)
    
    def set_custom_param(self, param_name: str, param_value: str) -> str:
        """
        Update a custom parameter in the params dictionary.

        :param param_name: The name of the parameter to set.
        :param param_value: The value of the parameter to set.
        """
        if param_name is not None:
            self.params[param_name] = param_value
            return f"Custom parameter '{param_name}' updated to: {param_value}"

class TechoneDataWSQuery(TechoneDataQuery):
    def __init__(self, auth_token: str, suite_id: str, warehouse_name: str, table_name: str, page_size: int = 50000, page: int = 1):
        """
        Subclass for Web Service (WS) queries.

        :param auth_token: The authentication token for the query.
        :param ws_endpoint: The Web Service endpoint for the query.
        :param page_size: The number of items per page (default is 50000).
        :param page: The page number to query (default is 1).
        """
        super().__init__(auth_token, page_size, page)
        self.params['p.SuiteId'] = suite_id
        self.params['p.WarehouseName'] = warehouse_name
        self.params['p.TableName'] = table_name
    
    def set_suite_id(self, new_suite_id: str) -> str:
        """
        Update the SuiteId value in the params dictionary.

        :param new_suite_id: The new SuiteId value to set.
        """
        self.params['p.SuiteId'] = new_suite_id
        return f"p.SuiteId updated to: {new_suite_id}"
    
    def set_table_name(self, new_table_name: str) -> str:
        """
        Update the TableName value in the params dictionary.

        :param new_table_name: The new TableName value to set.
        """
        self.params['p.TableName'] = new_table_name
        return f"p.TableName updated to: {new_table_name}"
    
    def set_warehouse_name(self, new_warehouse_name: str) -> str:
        """
        Update the WarehouseName value in the params dictionary.

        :param new_warehouse_name: The new WarehouseName value to set.
        """
        self.params['p.WarehouseName'] = new_warehouse_name
        return f"p.WarehouseName updated to: {new_warehouse_name}"

def _query_data_from_endpoint(endpoint_url, header, params) -> str:

    # Make the POST request to the authentication URL
    response = requests.get(endpoint_url, headers=header, params=params)
    
    # Return the entire response object
    return response

def _get_last_page_number(endpoint_url, header, params) -> int:
    last_page = 0
    response = _query_data_from_endpoint(endpoint_url, header, params)
    if response.status_code == 200 and 'TotalRecordCount' in json.loads(response.text):
        last_page = json.loads(response.text)['TotalRecordCount'] // params['pageSize'] + 1
    return last_page
