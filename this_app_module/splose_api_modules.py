import os
import requests
import logging
# import pandas as pd
# import numpy as np

# from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# # @retry(
# #     stop=stop_after_attempt(3),
# #     wait=wait_fixed(5),
# #     retry=retry_if_exception_type(Exception)
# # )
# def list_objects_from_splose(base_url: str, this_url: str, secret: str, accumulated_object_list = [], params = None) -> requests.Response:
#     """
#     Query data from the Splose API endpoint.
#     """
#     header_with_bearer_token_auth = {
#         'Authorization': 'Bearer ' + secret,
#         'Content-Type': 'application/json'
#     }
#     logging.info(f"Querying Splose API endpoint: {base_url}{this_url} with params: {params}")
#     response = requests.get(f"{base_url}{this_url}", headers=header_with_bearer_token_auth, params=params)
#     logging.info(f"Response status code: {response.status_code}")
#     if response.status_code != 200:
#         raise Exception(response.json())
#     # get the list of objects from the response
#     object_list = response.json().get('data', [])
#     # check if there is a next page link in the response
#     next_page_links = response.json().get('links', {})
#     logging.info(f"Number of objects retrieved: {len(object_list)}")
#     accumulated_object_list.extend(object_list)
#     # if next_page_links['nextPage'] is empty or does not exist, return response
#     if not next_page_links.get('nextPage') or not next_page_links.get('nextPage').startswith(this_url[:3]):
#         return accumulated_object_list
#     else:
#         return list_objects_from_splose(base_url, next_page_links['nextPage'], secret, accumulated_object_list)

# # @retry(
# #     stop=stop_after_attempt(3),
# #     wait=wait_fixed(5),
# #     retry=retry_if_exception_type(Exception)
# # )
# def get_one_object_from_splose(base_url: str, this_url: str, secret: str, object_id: int) -> requests.Response:
#     """
#     Query data from the Splose API endpoint for a single object.
#     """
#     header_with_bearer_token_auth = {
#         'Authorization': 'Bearer ' + secret,
#         'Content-Type': 'application/json'
#     }
#     response = requests.get(f"{base_url}{this_url}/{object_id}", headers=header_with_bearer_token_auth)
#     return response

# # @retry(
# #     stop=stop_after_attempt(3),
# #     wait=wait_fixed(5),
# #     retry=retry_if_exception_type(Exception)
# # )
# def create_one_object_in_splose(base_url: str, this_url: str, secret: str, object_data: dict) -> requests.Response:
#     """
#     Create a new object in Splose via the API endpoint.
#     """
#     header_with_bearer_token_auth = {
#         'Authorization': 'Bearer ' + secret,
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(f"{base_url}{this_url}", headers=header_with_bearer_token_auth, json=object_data)
#     return response

# def get_patient_to_contact_mapping() -> dict:
#     """
#     Get a mapping of patient IDs to contact IDs from Splose.
#     """
#     secret = os.environ["splose_api_secret"]
#     result_contact_list = list_objects_from_splose(
#         os.environ["splose_api_url"], 
#         os.environ["splose_api_url_list_contacts"], 
#         secret, [], params = {'include_archived': 'true'})
#     patient_to_contact_mapping  = {}
#     for contact in result_contact_list:
#         patient_id_list = contact.get('associatedPatientIds', [])
#         # convert all patient IDs to int first
#         patient_id_list = [int(pid) for pid in patient_id_list]
#         contact_id = contact.get('id')
#         # add the contact_id to each list by patient_id in the mapping
#         for patient_id in patient_id_list:
#             if patient_id not in patient_to_contact_mapping:
#                 patient_to_contact_mapping[str(patient_id)] = []
#             patient_to_contact_mapping[str(patient_id)].append(int(contact_id))
#     logging.info(f"Number of patient to contact mappings retrieved: {len(patient_to_contact_mapping)}")
#     return patient_to_contact_mapping

# # def get_all_awaiting_payment_invoices(patient_to_contact_mapping: dict) -> list:
# #     """
# #     Get all invoices with Awaiting Payment status from Splose.
# #     """
# #     secret = os.environ["splose_api_secret"]
# #     result_invoice_list = list_objects_from_splose(
# #         os.environ["splose_api_url"], 
# #         os.environ["splose_api_url_list_invoices"], 
# #         secret, [], params = {'status': 'Awaiting Payment'})
# #     logging.info(f"Number of invoices with Awaiting Payment status: {len(result_invoice_list)}")
# #     result_contact_list = list_objects_from_splose(
# #         os.environ["splose_api_url"], 
# #         os.environ["splose_api_url_list_contacts"], 
# #         secret, [], params = {'include_archived': 'true'})
# #     logging.info(f"Number of contacts retrieved: {len(result_contact_list)}")
# #     result_patient_list = list_objects_from_splose(
# #         os.environ["splose_api_url"], 
# #         os.environ["splose_api_url_list_patients"], 
# #         secret, [], params = {'include_archived': 'true'})
# #     logging.info(f"Number of patients retrieved: {len(result_patient_list)}")
# #     result_practitioner_list = list_objects_from_splose(
# #         os.environ["splose_api_url"], 
# #         os.environ["splose_api_url_list_practitioners"], 
# #         secret, [], params = {'include_archived': 'true'})
# #     logging.info(f"Number of practitioners retrieved: {len(result_practitioner_list)}")
# #     # convert result_invoice_list to a flat dataframe
# #     df_invoices = pd.json_normalize(result_invoice_list)
# #     df_contacts = pd.json_normalize(result_contact_list)
# #     df_patients = pd.json_normalize(result_patient_list)
# #     df_practitioners = pd.json_normalize(result_practitioner_list)
# #     if len(df_invoices) > 0:
# #         df_merged = df_invoices.merge(df_contacts[['id', 'name', 'companyName', 'email', 'phoneNumbers', 'addressL1', 'addressL2', 'addressL3', 'suburb', 'state', 'postalCode', 'country']].add_prefix('contact_'), how='left', left_on='contactId', right_on='contact_id')
# #         df_merged = df_merged.merge(df_patients[['id', 'firstname', 'lastname', 'preferredName', 'email', 'phoneNumbers', 'addressL1', 'addressL2', 'addressL3', 'city', 'state', 'postalCode', 'country', 'ndisNumber', 'ndisInfo', 'birthdate']].add_prefix('patient_'), how='left', left_on='patientId', right_on='patient_id')
# #         df_merged = df_merged.merge(df_practitioners[['id', 'firstname', 'lastname', 'providerNumbers']].add_prefix('practitioner_'), how='left', left_on='practitionerId', right_on='practitioner_id')
# #         df_merged = df_merged.drop(columns=['contact_id', 'patient_id', 'practitioner_id'])
# #         # convert id, patientId, contactId, locationId, practitionerId to int
# #         df_merged['id'] = df_merged['id'].astype(pd.Int64Dtype())
# #         df_merged['patientId'] = df_merged['patientId'].astype(pd.Int64Dtype())
# #         df_merged['locationId'] = df_merged['locationId'].astype(pd.Int64Dtype())
# #         df_merged['practitionerId'] = df_merged['practitionerId'].astype(pd.Int64Dtype())
# #         df_merged['contactId'] = df_merged['contactId'].astype(pd.Int64Dtype())
# #         # add a flag column 'contact_display_id' to keep track of the contact manipulations requested
# #         # default to 'SPL_C_' + str(contactId) if contactId is present indicating original Splose contact, otherwise set to nan
# #         df_merged['contact_display_id'] = df_merged['contactId'].apply(lambda x: f"SPL_C_{int(x)}" if pd.notna(x) else None)
# #         # also add a column 'contact_ndis_number' to keep track of the ndisNumber from patient
# #         df_merged['contact_ndis_number'] = df_merged['patient_ndisNumber']
# #         # also add a column 'contact_ndis_nominee_name' to keep track of the first and last names from the patient_ndisInfo object column if available
# #         df_merged['contact_ndis_nominee_name'] = None
# #         for idx, row in df_merged.iterrows():
# #             ndis_info = row['patient_ndisInfo']
# #             if ndis_info and isinstance(ndis_info, dict):
# #                 nominee_firstname = ndis_info.get('nomineeFirstName')
# #                 nominee_lastname = ndis_info.get('nomineeLastName')
# #                 if nominee_firstname and nominee_lastname:
# #                     nominee_name = f"{nominee_firstname} {nominee_lastname}"
# #                     df_merged.at[idx, 'contact_ndis_nominee_name'] = nominee_name
# #         # check and calculate based on manipulation rules:
# #         # 1. use the first letter in reference to categorize types of invoices (N - NDIS, H or S - SAH, P - PRIVATE)
# #         df_merged['invoice_type'] = df_merged['reference'].str[0].map({
# #             'N': 'NDIS',
# #             'H': 'SAH',
# #             'S': 'SAH',
# #             'P': 'PRIVATE'
# #         })
# #         # 2. for NDIS and PRIVATE invoices, if contactId is missing, then use patient data to populate into contact values, 
# #         for idx, row in df_merged.iterrows():
# #             if row['invoice_type'] in ['NDIS', 'PRIVATE'] and pd.isna(row['contactId']):
# #                 df_merged.at[idx, 'contact_name'] = f"{row['patient_firstname']} {row['patient_lastname']}"
# #                 df_merged.at[idx, 'contact_email'] = row['patient_email']
# #                 df_merged.at[idx, 'contact_phoneNumbers'] = row['patient_phoneNumbers']
# #                 df_merged.at[idx, 'contact_addressL1'] = row['patient_addressL1']
# #                 df_merged.at[idx, 'contact_addressL2'] = row['patient_addressL2']
# #                 df_merged.at[idx, 'contact_addressL3'] = row['patient_addressL3']
# #                 df_merged.at[idx, 'contact_suburb'] = row['patient_city']
# #                 df_merged.at[idx, 'contact_state'] = row['patient_state']
# #                 df_merged.at[idx, 'contact_postalCode'] = row['patient_postalCode']
# #                 df_merged.at[idx, 'contact_country'] = row['patient_country']
# #                 df_merged.at[idx, 'contact_display_id'] = 'SPL_P_' + str(row['patientId'])
# #         # 3. for SAH invoices, if contactId is missing, then use patientId to find the first associated contactId from patient_to_contact_mapping
# #         for idx, row in df_merged.iterrows():
# #             if row['invoice_type'] == 'SAH' and pd.isna(row['contactId']):
# #                 patient_id_str = str(row['patientId'])
# #                 associated_contact_ids = patient_to_contact_mapping.get(patient_id_str, [])
# #                 if len(associated_contact_ids) > 0:
# #                     contact_id_to_use = associated_contact_ids[0]
# #                     contact_row = df_contacts[df_contacts['id'] == contact_id_to_use]
# #                     if not contact_row.empty:
# #                         df_merged.at[idx, 'contact_name'] = contact_row.iloc[0]['name']
# #                         df_merged.at[idx, 'contact_companyName'] = contact_row.iloc[0]['companyName']
# #                         df_merged.at[idx, 'contact_email'] = contact_row.iloc[0]['email']
# #                         df_merged.at[idx, 'contact_phoneNumbers'] = contact_row.iloc[0]['phoneNumbers']
# #                         df_merged.at[idx, 'contact_addressL1'] = contact_row.iloc[0]['addressL1']
# #                         df_merged.at[idx, 'contact_addressL2'] = contact_row.iloc[0]['addressL2']
# #                         df_merged.at[idx, 'contact_addressL3'] = contact_row.iloc[0]['addressL3']
# #                         df_merged.at[idx, 'contact_suburb'] = contact_row.iloc[0]['suburb']
# #                         df_merged.at[idx, 'contact_state'] = contact_row.iloc[0]['state']
# #                         df_merged.at[idx, 'contact_postalCode'] = contact_row.iloc[0]['postalCode']
# #                         df_merged.at[idx, 'contact_country'] = contact_row.iloc[0]['country']
# #                         df_merged.at[idx, 'contact_display_id'] = f"SPL_C_{contact_id_to_use}"
# #         # sort the dataframe by due_date ascending
# #         df_merged = df_merged.sort_values(by=['dueDate'])
# #         # convert the dataframe df_merged to a list of dictionaries, and use None values to replace np.float64 NaN values
# #         result_list = df_merged.replace({np.nan: None}).to_dict(orient='records')
# #         logging.info("Invoices with Awaiting Payment status successfully processed.")
# #     else:
# #         logging.info("No invoices with Awaiting Payment status found.")
# #     return result_list

# def filter_for_invoices(invoice_list: list, invoice_filter_id_list: list) -> list:
#     """
#     Filter function to get only invoices with Awaiting Payment status.
#     """
#     # invoice_filter_id_list is a list of invoice IDs to filter for - in the type of int
#     filtered_invoices = [invoice for invoice in invoice_list if invoice['id'] in invoice_filter_id_list]
#     return filtered_invoices

# def update_invoices_with_payments(invoice_list: list, payment_dict: dict) -> list:
#     """
#     Compose invoices with their corresponding payments.
#     """
#     # payment list is a list of dictionaries with the structure
#     # {'invoiceNumber_0001': {'amount': 100.0, 'paymentDate': '2023-01-01'}, 'invoiceNumber_0002': {'amount': 250.0, 'paymentDate': '2023-01-02'}, ...}
#     # iterate through the invoice list and add new keys of 'amount' if there is a matching payment in the payment list
#     successful_list = []
#     for invoice in invoice_list:
#         if str(invoice['invoiceNumber']) in payment_dict:
#             # create a payment record based on the invoice and payment_dict[str(invoice['id'])]
#             this_payment_record = {
#                 'patientId': invoice['patientId'],
#                 'locationId': invoice['locationId'],
#                 'paymentMethodId': 38158, # assuming a default payment method ID
#                 'amount': payment_dict[str(invoice['invoiceNumber'])]['amount'],
#                 'paymentDate': payment_dict[str(invoice['invoiceNumber'])]['paymentDate'],
#                 'paymentInvoices': [
#                     {
#                     'invoiceId': invoice['id'],
#                     'amount': payment_dict[str(invoice['invoiceNumber'])]['amount']
#                     }
#                 ]
#             }
#             # and then call create_one_object_in_splose to create the payment in Splose
#             response = create_one_object_in_splose(
#                 os.environ["splose_api_url"], 
#                 os.environ["splose_api_url_list_payments"],
#                 os.environ["splose_api_secret"],
#                 this_payment_record
#             )
#             if response.status_code == 201:
#                 successful_list.append(invoice['invoiceNumber'])
#                 logging.info(f"Successfully created payment for invoice Number {invoice['invoiceNumber']}")
#             else:
#                 logging.error(f"Failed to create payment for invoice Number {invoice['invoiceNumber']}: {response.json()}")
#     return successful_list

# def update_invoices_with_payment_gaps(invoice_list: list, payment_dict: dict) -> list:
#     """
#     Compose invoices with their corresponding payments.
#     """
#     # payment list is a list of dictionaries with the structure
#     # {'invoiceNumber_0001': {'amount': 100.0, 'paymentDate': '2023-01-01'}, 'invoiceNumber_0002': {'amount': 250.0, 'paymentDate': '2023-01-02'}, ...}
#     # iterate through the invoice list and add new keys of 'amount' if there is a matching payment in the payment list
#     successful_list = []
#     for invoice in invoice_list:
#         if (str(invoice['invoiceNumber']) in payment_dict) and (invoice['paidAmount'] < invoice['total']):
#             # create a payment record based on the invoice and payment_dict[str(invoice['id'])]
#             this_payment_record = {
#                 'patientId': invoice['patientId'],
#                 'locationId': invoice['locationId'],
#                 'paymentMethodId': 38157, # assuming a default payment method ID
#                 'amount': round(invoice['total'] - invoice['paidAmount'], 2),  # round to 2 decimal places
#                 'paymentDate': payment_dict[str(invoice['invoiceNumber'])]['paymentDate'],
#                 'paymentInvoices': [
#                     {
#                     'invoiceId': invoice['id'],
#                     'amount': round(invoice['total'] - invoice['paidAmount'], 2)
#                     }
#                 ]
#             }
#             # and then call create_one_object_in_splose to create the payment in Splose
#             response = create_one_object_in_splose(
#                 os.environ["splose_api_url"], 
#                 os.environ["splose_api_url_list_payments"],
#                 os.environ["splose_api_secret"],
#                 this_payment_record
#             )
#             if response.status_code == 201:
#                 successful_list.append(invoice['invoiceNumber'])
#                 logging.info(f"Successfully created payment for invoice Number {invoice['invoiceNumber']}")
#             else:
#                 logging.error(f"Failed to create payment for invoice Number {invoice['invoiceNumber']}: {response.json()}")
#     return successful_list