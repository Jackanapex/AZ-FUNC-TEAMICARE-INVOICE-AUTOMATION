import os
import requests
import logging
import pandas as pd
import numpy as np

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(20),
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
    wait=wait_fixed(10),
    retry=retry_if_exception_type(Exception)
)
def get_one_object_from_splose(base_url: str, this_url: str, secret: str, object_id: int) -> requests.Response:
    """
    Query data from the Splose API endpoint for a single object.
    """
    header_with_bearer_token_auth = {
        'Authorization': 'Bearer ' + secret,
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{base_url}{this_url}/{object_id}", headers=header_with_bearer_token_auth)
    return response

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(10),
    retry=retry_if_exception_type(Exception)
)
def create_one_object_in_splose(base_url: str, this_url: str, secret: str, object_data: dict) -> requests.Response:
    """
    Create a new object in Splose via the API endpoint.
    """
    header_with_bearer_token_auth = {
        'Authorization': 'Bearer ' + secret,
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{base_url}{this_url}", headers=header_with_bearer_token_auth, json=object_data)
    return response

def get_patient_to_contact_mapping() -> dict:
    """
    Get a mapping of patient IDs to contact IDs from Splose.
    """
    secret = os.environ["splose_api_secret"]
    result_contact_list = list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_contacts"], 
        secret, [], params = {'include_archived': 'true'})
    patient_to_contact_mapping  = {}
    for contact in result_contact_list:
        patient_id_list = contact.get('associatedPatientIds', [])
        # convert all patient IDs to int first
        patient_id_list = [int(pid) for pid in patient_id_list]
        contact_id = contact.get('id')
        # add the contact_id to each list by patient_id in the mapping
        for patient_id in patient_id_list:
            if patient_id not in patient_to_contact_mapping:
                patient_to_contact_mapping[str(patient_id)] = []
            patient_to_contact_mapping[str(patient_id)].append(int(contact_id))
    logging.info(f"Number of patient to contact mappings retrieved: {len(patient_to_contact_mapping)}")
    return patient_to_contact_mapping

def get_all_awaiting_payment_invoices(patient_to_contact_mapping: dict) -> list:
    """
    Get all invoices with Awaiting Payment status from Splose.
    """
    secret = os.environ["splose_api_secret"]
    result_invoice_list = list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_invoices"], 
        secret, [], params = {'status': 'Awaiting Payment'})
    logging.info(f"Number of invoices with Awaiting Payment status: {len(result_invoice_list)}")
    result_contact_list = list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_contacts"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of contacts retrieved: {len(result_contact_list)}")
    result_patient_list = list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_patients"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of patients retrieved: {len(result_patient_list)}")
    result_practitioner_list = list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_practitioners"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of practitioners retrieved: {len(result_practitioner_list)}")
    # convert result_invoice_list to a flat dataframe
    df_invoices = pd.json_normalize(result_invoice_list)
    df_contacts = pd.json_normalize(result_contact_list)
    df_patients = pd.json_normalize(result_patient_list, max_level=0)
    df_practitioners = pd.json_normalize(result_practitioner_list)
    if len(df_invoices) > 0:
        df_merged = df_invoices.merge(df_contacts[['id', 'name', 'companyName', 'email', 'phoneNumbers', 'addressL1', 'addressL2', 'addressL3', 'suburb', 'state', 'postalCode', 'country']].add_prefix('contact_'), how='left', left_on='contactId', right_on='contact_id')
        df_merged = df_merged.merge(df_patients[['id', 'firstname', 'lastname', 'preferredName', 'email', 'phoneNumbers', 'addressL1', 'addressL2', 'addressL3', 'city', 'state', 'postalCode', 'country', 'ndisNumber', 'ndisInfo', 'birthdate']].add_prefix('patient_'), how='left', left_on='patientId', right_on='patient_id')
        df_merged = df_merged.merge(df_practitioners[['id', 'firstname', 'lastname', 'providerNumbers']].add_prefix('practitioner_'), how='left', left_on='practitionerId', right_on='practitioner_id')
        df_merged = df_merged.drop(columns=['contact_id', 'patient_id', 'practitioner_id'])
        # convert id, patientId, contactId, locationId, practitionerId to int
        df_merged['id'] = df_merged['id'].astype(pd.Int64Dtype())
        df_merged['patientId'] = df_merged['patientId'].astype(pd.Int64Dtype())
        df_merged['locationId'] = df_merged['locationId'].astype(pd.Int64Dtype())
        df_merged['practitionerId'] = df_merged['practitionerId'].astype(pd.Int64Dtype())
        df_merged['contactId'] = df_merged['contactId'].astype(pd.Int64Dtype())
        # add a flag column 'contact_display_id' to keep track of the contact manipulations requested
        # default to 'SPL_C_' + str(contactId) if contactId is present indicating original Splose contact, otherwise set to nan
        df_merged['contact_display_id'] = df_merged['contactId'].apply(lambda x: f"SPL_C_{int(x)}" if pd.notna(x) else None)
        # also add a column 'contact_ndis_number' to keep track of the ndisNumber from patient
        df_merged['contact_ndis_number'] = df_merged['patient_ndisNumber']
        # also add a column 'contact_ndis_nominee_name' to keep track of the first and last names from the patient_ndisInfo object column if available
        df_merged['contact_ndis_nominee_name'] = None
        for idx, row in df_merged.iterrows():
            ndis_info = row['patient_ndisInfo']
            if ndis_info and isinstance(ndis_info, dict):
                nominee_firstname = ndis_info.get('nomineeFirstName')
                nominee_lastname = ndis_info.get('nomineeLastName')
                if nominee_firstname and nominee_lastname:
                    nominee_name = f"{nominee_firstname} {nominee_lastname}"
                    df_merged.at[idx, 'contact_ndis_nominee_name'] = nominee_name
        # check and calculate based on manipulation rules:
        # 1. use the first letter in reference to categorize types of invoices (N - NDIS, H or S - SAH, P - PRIVATE)
        df_merged['invoice_type'] = df_merged['reference'].str[0].map({
            'N': 'NDIS',
            'H': 'SAH',
            'S': 'SAH',
            'P': 'PRIVATE'
        })
        # 2. for NDIS and PRIVATE invoices, if contactId is missing, then use patient data to populate into contact values, 
        for idx, row in df_merged.iterrows():
            if row['invoice_type'] in ['NDIS', 'PRIVATE'] and pd.isna(row['contactId']):
                df_merged.at[idx, 'contact_name'] = f"{row['patient_firstname']} {row['patient_lastname']}"
                df_merged.at[idx, 'contact_email'] = row['patient_email']
                df_merged.at[idx, 'contact_phoneNumbers'] = row['patient_phoneNumbers']
                df_merged.at[idx, 'contact_addressL1'] = row['patient_addressL1']
                df_merged.at[idx, 'contact_addressL2'] = row['patient_addressL2']
                df_merged.at[idx, 'contact_addressL3'] = row['patient_addressL3']
                df_merged.at[idx, 'contact_suburb'] = row['patient_city']
                df_merged.at[idx, 'contact_state'] = row['patient_state']
                df_merged.at[idx, 'contact_postalCode'] = row['patient_postalCode']
                df_merged.at[idx, 'contact_country'] = row['patient_country']
                df_merged.at[idx, 'contact_display_id'] = 'SPL_P_' + str(row['patientId'])
        # 3. for SAH invoices, if contactId is missing, then use patientId to find the first associated contactId from patient_to_contact_mapping
        for idx, row in df_merged.iterrows():
            if row['invoice_type'] == 'SAH' and pd.isna(row['contactId']):
                patient_id_str = str(row['patientId'])
                associated_contact_ids = patient_to_contact_mapping.get(patient_id_str, [])
                if len(associated_contact_ids) > 0:
                    contact_id_to_use = associated_contact_ids[0]
                    contact_row = df_contacts[df_contacts['id'] == contact_id_to_use]
                    if not contact_row.empty:
                        df_merged.at[idx, 'contact_name'] = contact_row.iloc[0]['name']
                        df_merged.at[idx, 'contact_companyName'] = contact_row.iloc[0]['companyName']
                        df_merged.at[idx, 'contact_email'] = contact_row.iloc[0]['email']
                        df_merged.at[idx, 'contact_phoneNumbers'] = contact_row.iloc[0]['phoneNumbers']
                        df_merged.at[idx, 'contact_addressL1'] = contact_row.iloc[0]['addressL1']
                        df_merged.at[idx, 'contact_addressL2'] = contact_row.iloc[0]['addressL2']
                        df_merged.at[idx, 'contact_addressL3'] = contact_row.iloc[0]['addressL3']
                        df_merged.at[idx, 'contact_suburb'] = contact_row.iloc[0]['suburb']
                        df_merged.at[idx, 'contact_state'] = contact_row.iloc[0]['state']
                        df_merged.at[idx, 'contact_postalCode'] = contact_row.iloc[0]['postalCode']
                        df_merged.at[idx, 'contact_country'] = contact_row.iloc[0]['country']
                        df_merged.at[idx, 'contact_display_id'] = f"SPL_C_{contact_id_to_use}"
        # sort the dataframe by due_date ascending
        df_merged = df_merged.sort_values(by=['dueDate'])
        # convert the dataframe df_merged to a list of dictionaries, and use None values to replace np.float64 NaN values
        result_list = df_merged.replace({np.nan: None}).to_dict(orient='records')
        logging.info("Invoices with Awaiting Payment status successfully processed.")
    else:
        logging.info("No invoices with Awaiting Payment status found.")
    return result_list

def filter_for_ndia_managed_invoices(invoice_list: list) -> list:
    """
    Filter function to get only invoices with NDIS management.
    """
    filtered_invoices = [invoice for invoice in invoice_list if ((invoice.get('patient_ndisInfo', {}) or {}).get('fundManagement', '') or '').upper() == 'NDIA-MANAGED']
    return filtered_invoices

def convert_invoice_list_to_ndia_required_format(invoice_list: list, appointment_list: list, service_list: list, support_item_list: list) -> list:
    result_ndia_invoice_list = []
    for invoice in invoice_list:
        for item in invoice.get('invoiceItems', []) or []:
            # firstly get the corresponding appointment or support item information
            this_support_item = None
            this_appointment = None
            if (item.get('type', '') or '') == 'appointment':
                this_appointment = next((a for a in appointment_list if a.get('id', -1) == item.get('typeId', -2)), None)
            elif (item.get('type', '') or '') == 'supportItem':
                this_support_item = next((s for s in support_item_list if s.get('id', -1) == item.get('typeId', -2)), None)
                this_appointment = next((a for a in appointment_list if a.get('id', -1) == this_support_item.get('appointmentId', -2)), None)
            # now based on the support item or appointment, calculate the Quantity, Hours, ClaimType and CancellationReason
            # then check this_appointment status in its appointmentPatients field matching element with patientId
            this_appointment_patient_status = next(
                (
                    (ap.get('status', 'Completed') or 'Completed') for ap in (this_appointment.get('appointmentPatients', []) or []) 
                    if ap.get('patientId', -1) == invoice.get('patientId', -2)
                ), 
                'Completed'
            ) if this_appointment else 'Completed'
            # then get the service type by differentiating between appointment and support item
            # if this_support_item is not None, then get the value under 'type' key in this_support_item
            this_service_type = 'NA'
            service_name = ''
            if this_support_item:
                service_name = this_support_item.get('type', '') or ''
            elif this_appointment: # elif it's an appointment item, get the serviceId from appointment and then find the service type from service_list
                service_obj = next((s for s in service_list if s.get('id', -1) == this_appointment.get('serviceId', -2)), None)
                if service_obj:
                    service_name = str(service_obj.get('id', -1) or -1)
            # Now define an arbitary dictionary between service name and NDIA service type code
            # TO-DO recommend to Xin to use a tag in the service to reflect NDIA service type directly, so this thing won't need to be
            # defined in code
            SERVICE_TO_NDIA_TYPE_MAPPING = {
                'Provider Travel': 'EMPTY',
                "122949": "EMPTY",
                "123661": "EMPTY",
                "123663": "EMPTY",
                "208278": "EMPTY",
                "208284": "EMPTY",
                "208285": "EMPTY",
                "233064": "EMPTY",
                "233065": "EMPTY",
                "233066": "EMPTY",
                "361982": "EMPTY",
                "361984": "EMPTY",
                "362028": "EMPTY",
                "362029": "EMPTY",
                "362409": "EMPTY",
                "362410": "EMPTY",
                "370323": "EMPTY",
                "370324": "EMPTY",
                "370325": "EMPTY",
                "381096": "EMPTY",
                "381097": "EMPTY",
                "381285": "EMPTY",
                "409770": "EMPTY",
                "409771": "EMPTY",
                "409772": "EMPTY",
                "409783": "EMPTY",
                "409784": "EMPTY",
                "409786": "EMPTY",
                "415901": "EMPTY",
                "415904": "EMPTY",
                "479983": "EMPTY",
                "479984": "EMPTY",
                "480006": "EMPTY",
                "480008": "EMPTY",
                "480011": "EMPTY",
                "480014": "EMPTY",
                "480016": "EMPTY",
                "480030": "EMPTY",
                "480033": "EMPTY",
                "480042": "EMPTY",
                "480045": "EMPTY",
                "480055": "EMPTY",
                "480057": "EMPTY",
                "480060": "EMPTY",
                "480062": "EMPTY",
                "494113": "EMPTY"
            }
            this_service_type = SERVICE_TO_NDIA_TYPE_MAPPING.get(service_name[:15], 'NA') or 'NA'
            this_service_type = '' if this_service_type == 'EMPTY' else this_service_type
            # now check if this_appointment_patient_status is Did not arrive or Cancelled, if either value, change this_service_type to CANC
            if this_appointment_patient_status == 'Did not arrive':
                this_service_type = 'CANC'
                this_cancellation_reason = 'NSDH'
            elif this_appointment_patient_status == 'Cancelled':
                this_service_type = 'CANC'
                this_cancellation_reason = 'NSDO'
            # now determine if the unit and unit price for the appointment/support item is quantity-based or hour-based
            this_unit = {
                'quantity_based': {'quantity': None, 'unit_price': None},
                'hour_based': {'quantity': None, 'unit_price': None}
            }
            if this_support_item:
                if (this_support_item.get('unit', '') or '').upper() == 'KM':
                    this_unit['quantity_based']['quantity'] = item.get('quantity', 1) or 1
                    this_unit['quantity_based']['unit_price'] = item.get('unitPrice', 0.0) or 0.0
                else:
                    this_unit['hour_based']['quantity'] = item.get('quantity', 1) or 1
                    this_unit['hour_based']['unit_price'] = item.get('unitPrice', 0.0) or 0.0
            elif this_appointment:
                if (this_appointment.get('unit', '') or '').upper() == 'HOUR':
                    this_unit['hour_based']['quantity'] = item.get('quantity', 1) or 1
                    this_unit['hour_based']['unit_price'] = item.get('unitPrice', 0.0) or 0.0
                else:
                    this_unit['quantity_based']['quantity'] = item.get('quantity', 1) or 1
                    this_unit['quantity_based']['unit_price'] = item.get('unitPrice', 0.0) or 0.0
            # now convert this_unit['hour_based']['quantity'] from number of hours to the format of HH:MM
            if this_unit['hour_based']['quantity'] is not None:
                total_hours = this_unit['hour_based']['quantity']
                hours_part = int(total_hours)
                minutes_part = int(round((total_hours - hours_part) * 60))
                this_unit['hour_based']['quantity'] = f"{hours_part:02d}:{minutes_part:02d}"
            # finally, compose the ndia_invoice_record
            ndia_invoice_record = {}
            ndia_invoice_record['RegistrationNumber'] = os.environ.get('ndia_registration_number', '')
            ndia_invoice_record['NDISNumber'] = invoice.get('patient_ndisNumber', '') or ''
            ndia_invoice_record['SupportsDeliveredFrom'] = (this_appointment.get('start', '') or '')[:10] if this_appointment else ''
            ndia_invoice_record['SupportsDeliveredTo'] = (this_appointment.get('end', '') or '')[:10] if this_appointment else ''
            ndia_invoice_record['SupportNumber'] = item.get('code', '') or ''
            ndia_invoice_record['ClaimReference'] = f"{invoice.get('invoiceNumber', 'NA') or 'NA'}_{item.get('id', 'NA') or 'NA'}"
            ndia_invoice_record['Quantity'] = this_unit['quantity_based']['quantity']
            ndia_invoice_record['Hours'] = this_unit['hour_based']['quantity']
            ndia_invoice_record['UnitPrice'] = item.get('unitPrice', 0.0) or 0.0
            ndia_invoice_record['GSTCode'] = 'P2'
            ndia_invoice_record['AuthorisedBy'] = None
            ndia_invoice_record['ParticipantApproved'] = None
            ndia_invoice_record['InKindFundingProgram'] = None
            ndia_invoice_record['ClaimType'] = this_service_type
            ndia_invoice_record['CancellationReason'] = this_cancellation_reason if this_service_type == 'CANC' else None
            ndia_invoice_record['ABN of Support Provider'] = os.environ.get('ndia_abn', '')
            result_ndia_invoice_list.append(ndia_invoice_record)
    return result_ndia_invoice_list

def list_all_appointment() -> list:
    resp = list_objects_from_splose(
        base_url = os.environ['splose_api_url'],
        this_url = os.environ['splose_api_url_list_appointments'],
        secret = os.environ['splose_api_secret']
    )
    assert(isinstance(resp, list))
    logging.info(f"Number of appointments retrieved: {len(resp)}")
    return resp

def list_all_service_with_code() -> list:
    resp = list_objects_from_splose(
        base_url = os.environ['splose_api_url'],
        this_url = os.environ['splose_api_url_list_services'],
        secret = os.environ['splose_api_secret']
    )
    assert(isinstance(resp, list))
    # services_with_code = [service for service in resp if (service.get('code', '') or '').strip() != '']
    logging.info(f"Number of services with code retrieved: {len(resp)}")
    return resp

def list_all_support_items_with_code() -> list:
    resp = list_objects_from_splose(
        base_url = os.environ['splose_api_url'],
        this_url = os.environ['splose_api_url_list_support_items'],
        secret = os.environ['splose_api_secret']
    )
    assert(isinstance(resp, list))
    # support_items_with_code = [support_item for support_item in resp if (support_item.get('itemCode', '') or '').strip() != '']
    logging.info(f"Number of support items with code retrieved: {len(resp)}")
    return resp

def create_ndia_invoice_list_csv(invoice_list: list) -> str:
    # get all appointments
    appointment_list = list_all_appointment()
    # get all services with code
    service_list = list_all_service_with_code()
    # get all support items with code
    support_item_list = list_all_support_items_with_code()
    # convert invoice list to ndia required format
    ndia_invoice_list = convert_invoice_list_to_ndia_required_format(invoice_list, appointment_list, service_list, support_item_list)
    logging.info(f"Number of NDIA invoice records created: {len(ndia_invoice_list)}")
    # now convert the ndia_invoice_list to a csv string
    df_ndia_invoices = pd.DataFrame(ndia_invoice_list)
    csv_string = df_ndia_invoices.to_csv(index=False)
    return csv_string

def filter_for_invoices(invoice_list: list, invoice_filter_id_list: list) -> list:
    """
    Filter function to get only invoices with Awaiting Payment status.
    """
    # invoice_filter_id_list is a list of invoice IDs to filter for - in the type of int
    filtered_invoices = [invoice for invoice in invoice_list if invoice['id'] in invoice_filter_id_list]
    return filtered_invoices

def update_invoices_with_payments(invoice_list: list, payment_dict: dict) -> list:
    """
    Compose invoices with their corresponding payments.
    """
    # payment list is a list of dictionaries with the structure
    # {'invoiceNumber_0001': {'amount': 100.0, 'paymentDate': '2023-01-01'}, 'invoiceNumber_0002': {'amount': 250.0, 'paymentDate': '2023-01-02'}, ...}
    # iterate through the invoice list and add new keys of 'amount' if there is a matching payment in the payment list
    successful_list = []
    for invoice in invoice_list:
        if (str(invoice['invoiceNumber']) in payment_dict) and (invoice['paidAmount'] < invoice['total']):
            # create a payment record based on the invoice and payment_dict[str(invoice['id'])]
            this_payment_record = {
                'patientId': invoice['patientId'],
                'locationId': invoice['locationId'],
                'paymentMethodId': 38158, # assuming a default payment method ID
                'amount': round(payment_dict[str(invoice['invoiceNumber'])]['amount'], 2),
                'paymentDate': payment_dict[str(invoice['invoiceNumber'])]['paymentDate'],
                'paymentInvoices': [
                    {
                    'invoiceId': invoice['id'],
                    'amount': round(
                        min(payment_dict[str(invoice['invoiceNumber'])]['amount'], invoice['total'] - invoice['paidAmount'])
                        , 2)
                    }
                ]
            }
            # and then call create_one_object_in_splose to create the payment in Splose
            response = create_one_object_in_splose(
                os.environ["splose_api_url"], 
                os.environ["splose_api_url_list_payments"],
                os.environ["splose_api_secret"],
                this_payment_record
            )
            if response.status_code == 201:
                successful_list.append(invoice['invoiceNumber'])
                logging.info(f"Successfully created payment for invoice Number {invoice['invoiceNumber']}")
            else:
                logging.error(f"Failed to create payment for invoice Number {invoice['invoiceNumber']}: {response.json()}")
    return successful_list

def update_invoices_with_payment_gaps(invoice_list: list, payment_dict: dict) -> list:
    """
    Compose invoices with their corresponding payments.
    """
    # payment list is a list of dictionaries with the structure
    # {'invoiceNumber_0001': {'amount': 100.0, 'paymentDate': '2023-01-01'}, 'invoiceNumber_0002': {'amount': 250.0, 'paymentDate': '2023-01-02'}, ...}
    # iterate through the invoice list and add new keys of 'amount' if there is a matching payment in the payment list
    successful_list = []
    for invoice in invoice_list:
        if (str(invoice['invoiceNumber']) in payment_dict) and (invoice['paidAmount'] < invoice['total']):
            # create a payment record based on the invoice and payment_dict[str(invoice['id'])]
            this_payment_record = {
                'patientId': invoice['patientId'],
                'locationId': invoice['locationId'],
                'paymentMethodId': 38157, # assuming a default payment method ID
                'amount': round(invoice['total'] - invoice['paidAmount'], 2),  # round to 2 decimal places
                'paymentDate': payment_dict[str(invoice['invoiceNumber'])]['paymentDate'],
                'paymentInvoices': [
                    {
                    'invoiceId': invoice['id'],
                    'amount': round(invoice['total'] - invoice['paidAmount'], 2)
                    }
                ]
            }
            # and then call create_one_object_in_splose to create the payment in Splose
            response = create_one_object_in_splose(
                os.environ["splose_api_url"], 
                os.environ["splose_api_url_list_payments"],
                os.environ["splose_api_secret"],
                this_payment_record
            )
            if response.status_code == 201:
                successful_list.append(invoice['invoiceNumber'])
                logging.info(f"Successfully created payment for invoice Number {invoice['invoiceNumber']}")
            else:
                logging.error(f"Failed to create payment for invoice Number {invoice['invoiceNumber']}: {response.json()}")
    return successful_list