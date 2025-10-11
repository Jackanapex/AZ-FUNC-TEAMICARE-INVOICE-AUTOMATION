import requests
import os
import json

def _get_bearer_token() -> dict:
    client_id = os.environ["livehire_client_id"]
    client_secret = os.environ["livehire_client_secret"]
    authentication_url = os.environ["livehire_authentication_url"]
    response = _authenticate(client_id, client_secret, authentication_url)
    if response:
        return {
            'body' : json.loads(response.text),
            'status_code' : response.status_code
        }
    else:
        return None

def _authenticate(client_id, client_secret, authentication_url):
    # Prepare the data payload
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    # Make the POST request to the authentication URL
    response = requests.post(authentication_url, data=data)
    
    # Return the entire response object
    return response