import requests

class LivehireDataQueryBuilder:
    def __init__(self, bearer_token: str) -> None:
        self.bearer_token = bearer_token
        self.query_header = {
            'Accept': 'text/csv',
            'Authorization': 'Bearer ' + self.bearer_token,
            'Content-Type': 'application/json'
        }
        self.query_body = {
            'pageNumber': 1
        }

    def set_fields(self, field_list) -> None:
        self.query_body['fields'] = field_list

    def add_filter(self, filter_dict) -> None:
        if 'filters' not in self.query_body:
            self.query_body['filters'] = []
        self.query_body['filters'].append(filter_dict)

    def set_page(self, target_page:int) -> None:
        self.query_body['pageNumber'] = target_page

def _compose_filter_dict(field_name: str, operator: str, value: str) -> dict:
    return {
        'column': field_name,
        'condition': operator,
        'value': value
    }

def _query_data_from_endpoint(endpoint_url, header, data):

    # Make the POST request to the authentication URL
    response = requests.post(endpoint_url, headers=header, json=data)
    
    # Return the entire response object
    return response

def _get_last_page_number(endpoint_url, header, data) -> int:
    while True:
        response = _query_data_from_endpoint(endpoint_url, header, data)
        if response.status_code != 200 or len(response.text.splitlines()) <= 2:
            break
        data['pageNumber'] += 1
    return data['pageNumber'] - 1

