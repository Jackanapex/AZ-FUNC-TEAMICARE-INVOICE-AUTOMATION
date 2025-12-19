import requests
import logging
import time
# import os
# from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
# from datetime import datetime

# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_fixed(5),
#     retry=retry_if_exception_type(Exception)
# )
# def refresh_access_token(url: str, client_id: str, client_secret: str, refresh_token: str, grant_type = 'refresh_token') -> dict:
#     """
#     Refresh the access token using the refresh token.
#     """
#     headers = {}
#     data = {
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'refresh_token': refresh_token,
#         'grant_type': grant_type
#     }
#     response = requests.post(url, headers=headers, data=data)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error refreshing access token: {response.text}")
#         response.raise_for_status()
#     return response.json()

# def create_get_access_code_url(url: str, client_id: str, redirect_uri: str, scope: str, response_type = 'code') -> str:
#     """
#     Get the access code using the authorization code.
#     """
#     # url-encode the redirect_uri
#     redirect_uri = requests.utils.quote(redirect_uri, safe='')
#     result_url = f"{url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}"
#     logging.info(f"Generated access code URL: {result_url}")
#     return result_url

# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_fixed(5),
#     retry=retry_if_exception_type(Exception)
# )
# def get_access_token(url: str, client_id: str, client_secret: str, code: str, redirect_uri: str, scope: str, grant_type = 'authorization_code') -> dict:
#     """
#     Get the access token using the authorization code.
#     """
#     # url-encode the redirect_uri
#     redirect_uri = requests.utils.quote(redirect_uri, safe='')
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     data = f"client_id={client_id}&client_secret={client_secret}&code={code}&redirect_uri={redirect_uri}&grant_type={grant_type}&scope={scope}"
#     response = requests.post(url, headers=headers, data=data)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting access token: {response.text}")
#         response.raise_for_status()
#     return response.json()

# def compose_request_headers(access_token: str) -> dict:
#     """
#     Compose the request headers for MYOB API calls.
#     """
#     headers = {
#         'Authorization': f"Bearer {access_token}",
#         'x-myobapi-key': os.environ.get('myob_client_id',''),
#         'x-myobapi-version': 'v2',
#         'Accept-Encoding': 'gzip,deflate'
#     }
#     return headers

# def get_company_info(access_token: str) -> dict:
#     """
#     Get the company info using the access token.
#     this is also used to verify if the access token is valid.
#     """
#     headers = compose_request_headers(access_token)
#     response = requests.get(f"{os.environ.get('myob_api_url','')}/{os.environ.get('myob_info_url','')}", headers=headers)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting company info: {response.text}")
#         response.raise_for_status()
#     return response.json()

# def get_contact_customer(access_token: str, business_id:str, display_id: str) -> dict:
#     """
#     Get the contact customer list using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer?$filter=DisplayID eq '{display_id}'"
#     logging.info(f"Getting contact customer from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting contact customer: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.json()

# def get_sale_invoice_service(access_token: str, business_id:str, number: str) -> dict:
#     """
#     Get the contact customer list using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item?$filter=Number eq '{number}'"
#     logging.info(f"Getting sale invoice service from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting sale invoice service: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.json()

# def recursively_get_customer_payments_after_date(access_token: str, business_id: str, after_date: datetime) -> list:
#     """
#     Recursively get the customer payments after a specific date using the access token.
#     """
#     after_date_str = f"Date gt DateTime'{after_date.strftime('%Y-%m-%dT%H:%M:%S')}'"
#     # url-encode after_date_str
#     after_date_str = requests.utils.quote(after_date_str, safe='')
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/CustomerPayment?$filter={after_date_str}"
#     logging.info(f"Getting customer payments from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting customer payments: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     payments = response.json()
#     all_payments = payments.get("Items", [])
#     # check if there is a next link
#     next_link = payments.get("NextLink")
#     while next_link:
#         logging.info(f"Getting next page of customer payments from URL: {next_link}")
#         response = requests.request("GET", next_link, headers=headers, data=payload)
#         logging.info(f"Response status code: {response.status_code}")
#         if response.status_code != 200:
#             logging.error(f"Error getting customer payments: {response.text}")
#             response.raise_for_status()
#         logging.info(f"Response text: {response.text}")
#         payments = response.json()
#         all_payments.extend(payments.get("Items", []))
#         next_link = payments.get("NextLink")
#     return all_payments

# def get_customer_payments_after_date_and_convert_to_invoice_key(access_token: str, business_id: str, after_date: datetime) -> dict:
#     """
#     Get the customer payments after a specific date using the access token.
#     """
#     after_date_str = f"Date gt DateTime'{after_date.strftime('%Y-%m-%dT%H:%M:%S')}'"
#     # url-encode after_date_str
#     after_date_str = requests.utils.quote(after_date_str, safe='')
#     payments = recursively_get_customer_payments_after_date(access_token, business_id, after_date)
#     # iterate through each item in payments['Items'] and extract the invoices under the Invoices key
#     invoice_payment_dict = {}
#     for payment in payments:
#         invoice_list = payment.get("Invoices", [])
#         for invoice in invoice_list:
#             invoice_number = invoice.get("Number")
#             if invoice_number is not None:
#                 if invoice_number not in invoice_payment_dict:
#                     invoice_payment_dict[str(invoice_number)] = {'amount': invoice.get('AmountApplied', 0.0), 'paymentDate': payment.get('Date', time.strftime("%Y-%m-%dT%H:%M:%S"))[:10]}
#                 else:
#                     invoice_payment_dict[str(invoice_number)]['amount'] += invoice.get('AmountApplied', 0.0)
#                     invoice_payment_dict[str(invoice_number)]['paymentDate'] = max(invoice_payment_dict[str(invoice_number)]['paymentDate'], payment.get('Date', time.strftime("%Y-%m-%dT%H:%M:%S"))[:10])
#     return invoice_payment_dict

# @retry(
#     stop=stop_after_attempt(5),
#     wait=wait_fixed(8),
#     retry=retry_if_exception_type(Exception)
# )
# def is_sale_invoice_service_existing_in_myob(access_token: str, business_id:str, splose_invoice_number: str) -> bool:
#     """
#     Check if a sale invoice service exists in MYOB using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item?$filter=Number eq '{splose_invoice_number}'"
#     logging.info(f"Checking sale invoice service existence from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error checking sale invoice service existence: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     invoices = response.json()
#     items = invoices.get("Items", [])
#     return len(items) > 0

# def post_contact_customer(access_token: str, business_id:str, customer_data: dict) -> bool:
#     """
#     Post a new contact customer using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer"
#     logging.info(f"Posting contact customer to URL: {url}")
#     payload = customer_data
#     headers = compose_request_headers(access_token)
#     response = requests.request("POST", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 201:
#         logging.error(f"Error posting contact customer: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.status_code == 201

# def post_sale_invoice_service(access_token: str, business_id:str, invoice_data: dict) -> bool:
#     """
#     Post a new sale invoice using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item"
#     logging.info(f"Posting sale invoice to URL: {url}")
#     payload = invoice_data
#     headers = compose_request_headers(access_token)
#     response = requests.request("POST", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 201:
#         logging.error(f"Error posting sale invoice: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.status_code == 201

# def put_contact_customer(access_token: str, business_id:str, customer_uid: str, customer_data: dict) -> bool:
#     """
#     Update an existing contact customer using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer/{customer_uid}"
#     logging.info(f"Putting contact customer to URL: {url}")
#     payload = customer_data
#     logging.info(f"Payload for PUT request: {payload}")
#     headers = compose_request_headers(access_token)
#     response = requests.request("PUT", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error putting contact customer: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.status_code == 200

# def put_sale_invoice_service(access_token: str, business_id:str, invoice_uid:str, invoice_data: dict) -> bool:
#     """
#     Post a new sale invoice using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item/{invoice_uid}"
#     logging.info(f"Putting sale invoice to URL: {url}")
#     payload = invoice_data
#     logging.info(f"Payload for PUT request: {payload}")
#     headers = compose_request_headers(access_token)
#     response = requests.request("PUT", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error putting sale invoice: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Response text: {response.text}")
#     return response.status_code == 200

# def delete_contact_customer(access_token: str, business_id:str, customer_uid: str) -> bool:
#     """
#     Delete an existing contact customer using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer/{customer_uid}"
#     logging.info(f"Deleting contact customer from URL: {url}")
#     payload = {
#         "UID": customer_uid
#     }
#     headers = compose_request_headers(access_token)
#     response = requests.request("DELETE", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error deleting contact customer: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Contact customer deleted successfully.")
#     return response.status_code == 200

# def delete_sale_invoice_service(access_token: str, business_id:str, invoice_uid: str) -> bool:
#     """
#     Delete an existing sale invoice service using the access token.
#     """
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item/{invoice_uid}"
#     logging.info(f"Deleting sale invoice service from URL: {url}")
#     payload = {
#         "UID": invoice_uid
#     }
#     headers = compose_request_headers(access_token)
#     response = requests.request("DELETE", url, headers=headers, json=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error deleting sale invoice service: {response.text}")
#         response.raise_for_status()
#     logging.info(f"Sale invoice service deleted successfully.")
#     return response.status_code == 200

# def upsert_contact_customer(access_token: str, business_id:str, customer_data: dict) -> bool:
#     """
#     Upsert a contact customer using the access token.
#     If the customer with the given display_id exists, update it.
#     Otherwise, create a new customer.
#     """
#     display_id = customer_data.get("DisplayID")
#     existing_customer = get_contact_customer(access_token, business_id, display_id)
#     items = existing_customer.get("Items", [])
#     if items:
#         customer_uid = items[0].get("UID")
#         # merge customer_data into items[0] except for the sub key of SellingDetails['TaxCode'] and SellingDetails['FreightTaxCode']
#         sellingdetails_taxcode_backup = items[0]["SellingDetails"]["TaxCode"]
#         sellingdetails_freighttaxcode_backup = items[0]["SellingDetails"]["FreightTaxCode"]
#         sellingdetails_taxcode_backup.update(customer_data["SellingDetails"]["TaxCode"])
#         sellingdetails_freighttaxcode_backup.update(customer_data["SellingDetails"]["FreightTaxCode"])
#         addresses_0_backup = items[0].get("Addresses", [{}])[0]
#         addresses_0_backup.update(customer_data.get("Addresses", [{}])[0])
#         items[0].update(customer_data)
#         items[0]["SellingDetails"]["TaxCode"] = sellingdetails_taxcode_backup
#         items[0]["SellingDetails"]["FreightTaxCode"] = sellingdetails_freighttaxcode_backup
#         items[0]["Addresses"][0] = addresses_0_backup
#         logging.info(f"Customer with DisplayID {display_id} exists. Updating customer UID: {customer_uid}")
#         return put_contact_customer(access_token, business_id, customer_uid, items[0])
#     else:
#         logging.info(f"Customer with DisplayID {display_id} does not exist. Creating new customer.")
#         return post_contact_customer(access_token, business_id, customer_data)

# def upsert_sale_invoice_service(access_token: str, business_id:str, invoice_data: dict) -> bool:
#     """
#     Upsert a contact customer using the access token.
#     If the customer with the given display_id exists, update it.
#     Otherwise, create a new customer.
#     """
#     number = invoice_data.get("Number")
#     existing_invoice = get_sale_invoice_service(access_token, business_id, number)
#     items = existing_invoice.get("Items", [])
#     if items:
#         invoice_uid = items[0].get("UID")
#         # merge invoice_data into items[0] except for the sub key of Terms
#         terms_backup = items[0].get("Terms", {})
#         terms_backup.update(invoice_data.get("Terms", {}))
#         items[0].update(invoice_data)
#         items[0]["Terms"] = terms_backup
#         logging.info(f"Invoice with Number {number} exists. Updating invoice UID: {invoice_uid}")
#         return put_sale_invoice_service(access_token, business_id, invoice_uid, items[0])
#     else:
#         logging.info(f"Invoice with Number {number} does not exist. Creating new invoice.")
#         return post_sale_invoice_service(access_token, business_id, invoice_data)

# def delete_contact_customers_without_display_id(access_token: str, business_id:str) -> list:
#     """
#     Delete all contact customers without a DisplayID using the access token.
#     """
#     url_encoded_filter_expression = requests.utils.quote("(DisplayID eq '') or (DisplayID eq null) or (endswith(DisplayID, 'TEST999') eq true)", safe='')
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Contact/Customer?$filter={url_encoded_filter_expression}"
#     logging.info(f"Getting contact customers without DisplayID from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting contact customers without DisplayID: {response.text}")
#         response.raise_for_status()
#     customers = response.json()
#     items = customers.get("Items", [])
#     delete_customers = []
#     for customer in items:
#         customer_uid = customer.get("UID")
#         if delete_contact_customer(access_token, business_id, customer_uid):
#             delete_customers.append(customer_uid)
#             logging.info(f"Deleted contact customer: {customer}")
#     logging.info(f"Deleted {len(delete_customers)} contact customers without DisplayID.")
#     return delete_customers

# def delete_sale_invoice_service_without_number(access_token: str, business_id:str) -> list:
#     """
#     Delete all contact customers without a DisplayID using the access token.
#     """
#     url_encoded_filter_expression = requests.utils.quote("(Number eq '') or (Number eq null) or (startswith(Number, 'PSMN') eq true)", safe='')
#     url = f"{os.environ.get('myob_api_url','')}/{business_id}/Sale/Invoice/Item?$filter={url_encoded_filter_expression}"
#     logging.info(f"Getting sale invoices without Number from URL: {url}")
#     payload = {}
#     headers = compose_request_headers(access_token)
#     response = requests.request("GET", url, headers=headers, data=payload)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         logging.error(f"Error getting sale invoices without Number: {response.text}")
#         response.raise_for_status()
#     invoices = response.json()
#     items = invoices.get("Items", [])
#     delete_invoices = []
#     for invoice in items:
#         invoice_uid = invoice.get("UID")
#         if delete_sale_invoice_service(access_token, business_id, invoice_uid):
#             delete_invoices.append(invoice_uid)
#             logging.info(f"Deleted sale invoice: {invoice}")
#     logging.info(f"Deleted {len(delete_invoices)} sale invoices without Number.")
#     return delete_invoices


# def convert_splose_invoice_to_myob_customer(access_token: str, business_id:str, splose_invoice_dict_list: list) -> dict:
#     customer_list = []
#     # iterate through splose_invoice_dict_list
#     # and create a customer dict if contact_display_id is not None, and it doesn't already exist in customer_list by checking DisplayID
#     for splose_invoice in splose_invoice_dict_list:
#         if splose_invoice.get('contact_display_id') is not None and not any(cust.get('DisplayID') == splose_invoice['contact_display_id'] for cust in customer_list):
#             # create customer dictionary
#             # if contact_ndis_number is not None, include it in the Notes
#             # if contact_ndis_nominee_name is not None, include it in the notes
#             note_string = ""
#             if splose_invoice.get('contact_display_id','').startswith('SPL_P_'):
#                 if splose_invoice.get('contact_ndis_number') is not None:
#                     note_string += f"NDIS Number: {splose_invoice['contact_ndis_number']}\n"
#                 if splose_invoice.get('contact_ndis_nominee_name') is not None:
#                     note_string += f"NDIS Nominee Name: {splose_invoice['contact_ndis_nominee_name']}\n"
#             # Because MYOB has 20 character limit on FirstName, and 30 character limit on LastName,
#             # we will split splose_invoice['contact_name'] by space and use the parts that add up to less than 20 characters for FirstName,
#             # and the rest for LastName.
#             name_parts = splose_invoice['contact_name'].split(" ")
#             first_name = ""
#             last_name = ""
#             for part in name_parts:
#                 if len(first_name) + len(part) + 1 <= 20:
#                     if first_name:
#                         first_name += " "
#                     first_name += part
#                 else:
#                     if last_name:
#                         last_name += " "
#                     last_name += part
#             customer_dict = {
#                 "DisplayID": splose_invoice['contact_display_id'],
#                 "LastName": f"{last_name} {splose_invoice['contact_companyName'] or ' '}".strip()[:30] or ' ',
#                 "FirstName": first_name or ' ',
#                 "IsIndividual": True,
#                 "IsActive": True,
#                 "Notes": note_string.strip(),
#                 "Addresses": [
#                 {
#                     "Street": f"{splose_invoice['contact_addressL1'] or ' '} {splose_invoice['contact_addressL2'] or ' '} {splose_invoice['contact_addressL3']or ' '}".strip(),
#                     "City": splose_invoice['contact_suburb'] or ' ',
#                     "State": splose_invoice['contact_state'] or ' ',
#                     "PostCode": splose_invoice['contact_postalCode'] or ' ',
#                     "Country": splose_invoice['contact_country'] or ' ',
#                     "Fax": "",
#                     "Email": splose_invoice['contact_email'],
#                     "Website": "",
#                     "ContactName": splose_invoice['contact_name'][:25] or ' ',
#                     "Salutation": "",
#                     "Phone1": splose_invoice.get('contact_phoneNumbers', [])[0]['phoneNumber'] if len(splose_invoice.get('contact_phoneNumbers', [])) > 0 else "",
#                     "Phone2": splose_invoice.get('contact_phoneNumbers', [])[1]['phoneNumber'] if len(splose_invoice.get('contact_phoneNumbers', [])) > 1 else "",
#                     "Phone3": splose_invoice.get('contact_phoneNumbers', [])[2]['phoneNumber'] if len(splose_invoice.get('contact_phoneNumbers', [])) > 2 else ""
#                 }],
#                 "SellingDetails": {
#                     "SaleLayout": "Item",
#                     "TaxCode": {
#                         "UID": os.environ.get("myob_gst_tax_uid","")
#                     },
#                     "FreightTaxCode": {
#                         "UID": os.environ.get("myob_gst_tax_uid","")
#                     },
#                     "Terms": {
#                         "PaymentIsDue": "InAGivenNumberOfDays",
#                         "BalanceDueDate": 7
#                     }
#                 }
#             }
#             customer_list.append(customer_dict)
#     logging.info(f"Total unique customers to upsert: {len(customer_list)}")
#     # upsert each customer in customer_list
#     # keep a result list of successfully upserted customers by DisplayID
#     successfully_upserted_customers = {}
#     for customer in customer_list:
#         logging.info(f"Upserting customer: {customer}")
#         if upsert_contact_customer(
#             access_token,
#             business_id,
#             customer
#         ):
#             successfully_upserted_customers[customer.get("DisplayID")] = None
#     # now retrieve the UID for each successfully upserted customer and add it to the result list
#     for customer in successfully_upserted_customers:
#         customer_record = get_contact_customer(
#             access_token,
#             business_id,
#             customer
#         )
#         successfully_upserted_customers[customer] = customer_record.get("Items",[{}])[0].get("UID", None)
#     # with this return joined to the invoice data, we have the customer UIDs to post these invoices against
#     return successfully_upserted_customers

# def convert_splose_invoice_to_myob_invoice(access_token: str, business_id:str, splose_invoice_dict_list: list, customer_uid_map: dict) -> dict:
#     invoice_list = []
#     # iterate through splose_invoice_dict_list
#     # and create a invoice dict if contact_display_id is not None, and it also exists as a key in customer_uid_map
#     # NOTE: when splose invoice contact genuinely missing, splose functions will try to supply a contact based on the
#     # invoice type. However, there are cases when an invoice type is not determinable. In such cases,
#     # if the contact is missing, the record will be skipped by this conversion function
#     # if the contact genuinely exists, the record will still be imported to MYOB under the UNKNOWN category
#     for splose_invoice in splose_invoice_dict_list:
#         if splose_invoice.get('contact_display_id') is not None and splose_invoice['contact_display_id'] in customer_uid_map:
#             this_invoice_type = splose_invoice.get('invoice_type','UNKNOWN') or 'UNKNOWN' 
#             if len(this_invoice_type) <= 0:
#                 this_invoice_type = 'UNKNOWN'
#             note_string_ndis = f"{splose_invoice.get('patient_firstname', '') or ' '} {splose_invoice.get('patient_lastname', '') or ' '}\nDOB: {(splose_invoice.get('patient_birthdate', '') or ' ')[:10]}".strip()
#             if splose_invoice.get('contact_ndis_number') is not None:
#                 note_string_ndis += f"\nNDIS Number: {splose_invoice['contact_ndis_number']}"
#             if splose_invoice.get('contact_ndis_nominee_name') is not None:
#                 note_string_ndis += f"\nNDIS Nominee Name: {splose_invoice['contact_ndis_nominee_name']}"
#             note_string_sah = f"Re: Support provided to {splose_invoice.get('patient_preferredName', '') or ' '} {splose_invoice.get('patient_firstname', '') or ' '} {splose_invoice.get('patient_lastname', '') or ' '}"
#             note_string_private = f"Re: Private care for {splose_invoice.get('patient_preferredName', '') or ' '} {splose_invoice.get('patient_firstname', '') or ' '} {splose_invoice.get('patient_lastname', '') or ' '}"
#             # first create invoice dictionary common fields among all 3 types
#             myob_invoice_dict = {
#                 "Number": splose_invoice.get('invoiceNumber',f"UNKNOWN-{int(time.time())}"[:12]),
#                 "CustomerPurchaseOrderNumber": splose_invoice.get('reference',''),
#                 # get updateAt from splose_invoice, if not present use current date and time in YYYY-MM-DDTHH:MM:SS format
#                 "Date": splose_invoice.get('updatedAt',time.strftime("%Y-%m-%dT%H:%M:%S")),
#                 "Customer": {
#                     "UID": customer_uid_map.get(splose_invoice['contact_display_id'], '')
#                 },
#                 "IsTaxInclusive": True,
#                 "Lines": [],
#                 "Category": {"UID": os.environ.get(f"myob_category_{this_invoice_type.lower()}_uid","")},
#                 "ShippingMethod": None,
#                 "JournalMemo": splose_invoice.get('id','UNKNOWN'),
#                 "Order": None
#             }
#             # then add invoice dictionary different fields based on splose_invoice['invoice_type']
#             # when type is NDIS
#             if this_invoice_type == 'NDIS':
#                 myob_invoice_dict['Comment'] = note_string_ndis.strip()
#                 myob_invoice_dict['Lines'] = [{
#                     "Type": "Transaction",
#                     "Description": f"{invoiceItem.get('type', '')}: {invoiceItem.get('description','No Description')}\nItem# {invoiceItem.get('code','No Code')}\nTherapist {splose_invoice.get('practitioner_firstname','No Firstname')} {splose_invoice.get('practitioner_lastname','No Lastname')}",
#                     "Account": {
#                         "UID": os.environ.get("myob_service_income_account_uid","")
#                     },
#                     "UnitOfMeasure" : "Hours",
#                     "UnitCount" : invoiceItem.get('quantity', 1),
#                     "UnitPrice" : invoiceItem.get('unitPrice', 0.00),
#                     "Job": None,
#                     "TaxCode": {
#                         "UID": os.environ.get("myob_gstfree_tax_uid","")
#                     }
#                 } for invoiceItem in splose_invoice.get('invoiceItems',[])]
#             # when type is SAH
#             elif this_invoice_type == 'SAH':
#                 myob_invoice_dict['Comment'] = note_string_sah.strip()
#                 myob_invoice_dict['Lines'] = [{
#                     "Type": "Transaction",
#                     "Description": f"{invoiceItem.get('type', '')}: {invoiceItem.get('description','No Description')}\nClinician {splose_invoice.get('practitioner_firstname','No Firstname')} {splose_invoice.get('practitioner_lastname','No Lastname')}\n{(splose_invoice.get('referenceNumbers',['']) or [''])[0]}",
#                     "Account": {
#                         "UID": os.environ.get("myob_service_income_account_uid","")
#                     },
#                     "UnitOfMeasure" : "Hours",
#                     "UnitCount" : invoiceItem.get('quantity', 1),
#                     "UnitPrice" : invoiceItem.get('unitPrice', 0.00),
#                     "Job": None,
#                     "TaxCode": {
#                         "UID": os.environ.get("myob_gstfree_tax_uid","")
#                     }
#                 } for invoiceItem in splose_invoice.get('invoiceItems',[])]
#             # when type is PRIVATE
#             elif this_invoice_type == 'PRIVATE':
#                 myob_invoice_dict['Comment'] = note_string_private.strip()
#                 myob_invoice_dict['Lines'] = [{
#                     "Type": "Transaction",
#                     "Description": f"{invoiceItem.get('type', '')}: {invoiceItem.get('description','No Description')}\nTherapist {splose_invoice.get('practitioner_firstname','No Firstname')} {splose_invoice.get('practitioner_lastname','No Lastname')}\n{(splose_invoice.get('referenceNumbers',['']) or [''])[0]}",
#                     "Account": {
#                         "UID": os.environ.get("myob_service_income_account_uid","")
#                     },
#                     "UnitOfMeasure" : "Hours",
#                     "UnitCount" : invoiceItem.get('quantity', 1),
#                     "UnitPrice" : invoiceItem.get('unitPrice', 0.00),
#                     "Job": None,
#                     "TaxCode": {
#                         "UID": os.environ.get("myob_gstfree_tax_uid","")
#                     }
#                 } for invoiceItem in splose_invoice.get('invoiceItems',[])]
#             # when type is UNKNOWN
#             else:
#                 myob_invoice_dict['Comment'] = "Service type UNKNOWN. Please review."
#                 myob_invoice_dict['Lines'] = [{
#                     "Type": "Transaction",
#                     "Description": f"{invoiceItem.get('type', '')}: {invoiceItem.get('description','No Description')}\nItem# {invoiceItem.get('code','No Code')}\nTherapist/Clinician {splose_invoice.get('practitioner_firstname','No Firstname')} {splose_invoice.get('practitioner_lastname','No Lastname')}\n{splose_invoice.get('referenceNumbers',[''])[0]}",
#                     "Account": {
#                         "UID": os.environ.get("myob_service_income_account_uid","")
#                     },
#                     "UnitOfMeasure" : "Hours",
#                     "UnitCount" : invoiceItem.get('quantity', 1),
#                     "UnitPrice" : invoiceItem.get('unitPrice', 0.00),
#                     "Job": None,
#                     "TaxCode": {
#                         "UID": os.environ.get("myob_gstfree_tax_uid","")
#                     }
#                 } for invoiceItem in splose_invoice.get('invoiceItems',[])]
#             # append the invoice dict to invoice_list
#             invoice_list.append(myob_invoice_dict)
#     logging.info(f"Total invoices to post: {len(invoice_list)}")
#     # though we have the upsert method available, for invoices we will only post new ones
#     # post each invoice in invoice_list
#     # and keep a result list of successfully posted invoices by Number
#     successfully_posted_invoices = {}
#     for invoice in invoice_list:
#         logging.info(f"Posting invoice: {invoice}")
#         if post_sale_invoice_service(
#             access_token,
#             business_id,
#             invoice
#         ):
#             successfully_posted_invoices[invoice.get("Number")] = True
#     # now add the invoiceNumber that is not successfully posted to the result dict with value of False
#     for splose_invoice in splose_invoice_dict_list:
#         if splose_invoice.get('invoiceNumber') is not None and splose_invoice['invoiceNumber'] not in successfully_posted_invoices:
#             successfully_posted_invoices[splose_invoice['invoiceNumber']] = False
#     return successfully_posted_invoices