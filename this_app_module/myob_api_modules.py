import requests
import logging
import time
import os
import base64
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def refresh_access_token(url: str, client_id: str, client_secret: str, refresh_token: str, grant_type = 'refresh_token') -> dict:
    """
    Refresh the access token using the refresh token.
    """
    headers = {}
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': grant_type
    }
    response = requests.post(url, headers=headers, data=data)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error refreshing access token: {response.text}")
        response.raise_for_status()
    return response.json()

def create_get_access_code_url(url: str, client_id: str, redirect_uri: str, scope: str, response_type = 'code') -> str:
    """
    Get the access code using the authorization code.
    """
    # url-encode the redirect_uri
    redirect_uri = requests.utils.quote(redirect_uri, safe='')
    result_url = f"{url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}"
    logging.info(f"Generated access code URL: {result_url}")
    return result_url

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def get_access_token(url: str, client_id: str, client_secret: str, code: str, redirect_uri: str, scope: str, grant_type = 'authorization_code') -> dict:
    """
    Get the access token using the authorization code.
    """
    # url-encode the redirect_uri
    redirect_uri = requests.utils.quote(redirect_uri, safe='')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = f"client_id={client_id}&client_secret={client_secret}&code={code}&redirect_uri={redirect_uri}&grant_type={grant_type}&scope={scope}"
    response = requests.post(url, headers=headers, data=data)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error getting access token: {response.text}")
        response.raise_for_status()
    return response.json()

def compose_request_headers(access_token: str) -> dict:
    """
    Compose the request headers for MYOB API calls.
    """
    headers = {
        'Authorization': f"Bearer {access_token}",
        'x-myobapi-key': os.environ.get('myob_client_id',''),
        'x-myobapi-version': 'v2',
        'Accept-Encoding': 'gzip,deflate'
    }
    return headers

def get_company_info(access_token: str) -> dict:
    """
    Get the company info using the access token.
    this is also used to verify if the access token is valid.
    """
    headers = compose_request_headers(access_token)
    response = requests.get(f"{os.environ.get('myob_api_url','')}/{os.environ.get('myob_info_url','')}", headers=headers)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error getting company info: {response.text}")
        response.raise_for_status()
    return response.json()

def get_contact_customer(access_token: str, business_id:str, display_id: str) -> dict:
    """
    Get the contact customer list using the access token.
    """
    url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer?$filter=DisplayID eq '{display_id}'"
    logging.info(f"Getting contact customer from URL: {url}")
    payload = {}
    headers = compose_request_headers(access_token)
    response = requests.request("GET", url, headers=headers, data=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error getting contact customer: {response.text}")
        response.raise_for_status()
    logging.info(f"Response text: {response.text}")
    return response.json()

def post_contact_customer(access_token: str, business_id:str, customer_data: dict) -> bool:
    """
    Post a new contact customer using the access token.
    """
    url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer"
    logging.info(f"Posting contact customer to URL: {url}")
    payload = customer_data
    headers = compose_request_headers(access_token)
    response = requests.request("POST", url, headers=headers, json=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 201:
        logging.error(f"Error posting contact customer: {response.text}")
        response.raise_for_status()
    logging.info(f"Response text: {response.text}")
    return response.status_code == 201

def put_contact_customer(access_token: str, business_id:str, customer_uid: str, customer_data: dict) -> bool:
    """
    Update an existing contact customer using the access token.
    """
    url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer/{customer_uid}"
    logging.info(f"Putting contact customer to URL: {url}")
    payload = customer_data
    headers = compose_request_headers(access_token)
    response = requests.request("PUT", url, headers=headers, json=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error putting contact customer: {response.text}")
        response.raise_for_status()
    logging.info(f"Response text: {response.text}")
    return response.status_code == 200

def delete_contact_customer(access_token: str, business_id:str, customer_uid: str) -> bool:
    """
    Delete an existing contact customer using the access token.
    """
    url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer/{customer_uid}"
    logging.info(f"Deleting contact customer from URL: {url}")
    payload = {
        "UID": customer_uid
    }
    headers = compose_request_headers(access_token)
    response = requests.request("DELETE", url, headers=headers, json=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error deleting contact customer: {response.text}")
        response.raise_for_status()
    logging.info(f"Contact customer deleted successfully.")
    return response.status_code == 200

def upsert_contact_customer(access_token: str, business_id:str, customer_data: dict) -> bool:
    """
    Upsert a contact customer using the access token.
    If the customer with the given display_id exists, update it.
    Otherwise, create a new customer.
    """
    display_id = customer_data.get("DisplayID")
    existing_customer = get_contact_customer(access_token, business_id, display_id)
    items = existing_customer.get("Items", [])
    if items:
        customer_uid = items[0].get("UID")
        # merge customer_data into items[0]
        items[0].update(customer_data)
        logging.info(f"Customer with DisplayID {display_id} exists. Updating customer UID: {customer_uid}")
        return put_contact_customer(access_token, business_id, customer_uid, items[0])
    else:
        logging.info(f"Customer with DisplayID {display_id} does not exist. Creating new customer.")
        return post_contact_customer(access_token, business_id, customer_data)
    
# TO-DO: add test case
def delete_contact_customers_without_display_id(access_token: str, business_id:str) -> list:
    """
    Delete all contact customers without a DisplayID using the access token.
    """
    url_encoded_filter_expression = requests.utils.quote("(DisplayID eq '') or (DisplayID eq null)", safe='')
    url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer?$filter={url_encoded_filter_expression}"
    logging.info(f"Getting contact customers without DisplayID from URL: {url}")
    payload = {}
    headers = compose_request_headers(access_token)
    response = requests.request("GET", url, headers=headers, data=payload)
    logging.info(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        logging.error(f"Error getting contact customers without DisplayID: {response.text}")
        response.raise_for_status()
    customers = response.json()
    items = customers.get("Items", [])
    delete_customers = []
    for customer in items:
        customer_uid = customer.get("UID")
        if delete_contact_customer(access_token, business_id, customer_uid):
            delete_customers.append(customer_uid)
            logging.info(f"Deleted contact customer: {customer}")
    logging.info(f"Deleted {len(delete_customers)} contact customers without DisplayID.")
    return delete_customers

def convert_splose_invoice_to_myob_customer(splose_invoice_dict_list: list) -> dict:
    customer_list = []
    # iterate through splose_invoice_dict_list
    # and create a customer dict if contact_display_id is not None, and it doesn't already exist in customer_list by checking DisplayID
    for splose_invoice in splose_invoice_dict_list:
        if splose_invoice.get('contact_display_id') is not None and not any(cust.get('DisplayID') == splose_invoice['contact_display_id'] for cust in customer_list):
            # create customer dictionary
            # if contact_ndis_number is not None, include it in the Notes
            # if contact_ndis_nominee_name is not None, include it in the notes
            note_string = ""
            if splose_invoice.get('contact_ndis_number') is not None:
                note_string += f"NDIS Number: {splose_invoice['contact_ndis_number']}\n"
            if splose_invoice.get('contact_ndis_nominee_name') is not None:
                note_string += f"NDIS Nominee Name: {splose_invoice['contact_ndis_nominee_name']}\n"
            customer_dict = {
                "DisplayID": splose_invoice['contact_display_id'],
                "LastName": splose_invoice['contact_companyName'],
                "FirstName": splose_invoice['contact_name'],
                "IsIndividual": True,
                "IsActive": True,
                "Notes": note_string.strip(),
                "Addresses": [
                {
                    "Street": f"{splose_invoice['contact_addressL1']} {splose_invoice['contact_addressL2']} {splose_invoice['contact_addressL3']}",
                    "City": splose_invoice['contact_suburb'],
                    "State": splose_invoice['contact_state'],
                    "PostCode": splose_invoice['contact_postalCode'],
                    "Country": splose_invoice['contact_country'],
                    "Fax": "",
                    "Email": splose_invoice['contact_email'],
                    "Website": "",
                    "ContactName": splose_invoice['contact_name'],
                    "Salutation": ""
                }],
                "SellingDetails": {
                    "SaleLayout": "Service",
                    "TaxCode": {
                        "UID": "1af16821-106a-4f1a-b1fa-469931588752"
                    },
                    "FreightTaxCode": {
                        "UID": "1af16821-106a-4f1a-b1fa-469931588752"
                    }
                }
            }
        customer_list.append(customer_dict)
    # upsert each customer in customer_list
    # keep a result list of successfully upserted customers by DisplayID
    successfully_upserted_customers = {}
    for customer in customer_list:
        logging.info(f"Upserting customer: {customer}")
        if upsert_contact_customer(
            access_token=os.environ.get('myob_access_token',''),
            business_id=os.environ.get('myob_business_id',''),
            customer_data=customer
        ):
            successfully_upserted_customers[customer.get("DisplayID")] = None
    # now retrieve the UID for each successfully upserted customer and add it to the result list
    for customer in successfully_upserted_customers:
        customer_record = get_contact_customer(
            access_token=os.environ.get('myob_access_token',''),
            business_id=os.environ.get('myob_business_id',''),
            display_id=customer
        )
        successfully_upserted_customers[customer] = customer_record.get("UID")
    # with this return joined to the invoice data, we have the customer UIDs to post these invoices against
    return successfully_upserted_customers