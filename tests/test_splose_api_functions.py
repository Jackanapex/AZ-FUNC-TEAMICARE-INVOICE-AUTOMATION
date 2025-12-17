# import azure.functions as func
# import os
# import datetime
# import json
# import logging
# from test_utils import MockTimer
# from test_utils import MockOut
# from test_utils import MockIn
# from test_utils import _save_json_result_to_local_csv_file

# def test_list_invoices_from_splose(entry):
#     resp = entry.splose_api_modules.list_objects_from_splose(
#         base_url = os.environ['splose_api_url'],
#         this_url = os.environ['splose_api_url_list_invoices'],
#         secret = os.environ['splose_api_secret'],
#         params = {'status': 'Awaiting Payment'}
#     )
#     assert(isinstance(resp, list))

# def test_list_contacts_from_splose(entry):
#     resp = entry.splose_api_modules.list_objects_from_splose(
#         base_url = os.environ['splose_api_url'],
#         this_url = os.environ['splose_api_url_list_contacts'],
#         secret = os.environ['splose_api_secret'],
#         params = {'include_archived': 'true'}
#     )
#     assert(isinstance(resp, list))
#     assert(len(resp) > 0)

# def test_list_patients_from_splose(entry):
#     resp = entry.splose_api_modules.list_objects_from_splose(
#         base_url = os.environ['splose_api_url'],
#         this_url = os.environ['splose_api_url_list_patients'],
#         secret = os.environ['splose_api_secret'],
#         params = {'include_archived': 'true'}
#     )
#     assert(isinstance(resp, list))
#     assert(len(resp) > 0)

# def test_list_practitioners_from_splose(entry):
#     resp = entry.splose_api_modules.list_objects_from_splose(
#         base_url = os.environ['splose_api_url'],
#         this_url = os.environ['splose_api_url_list_practitioners'],
#         secret = os.environ['splose_api_secret'],
#         params = {'include_archived': 'true'}
#     )
#     assert(isinstance(resp, list))
#     assert(len(resp) > 0)

# def test_post_a_payment_to_invoice(entry):
#     # first get a list of invoices with Awaiting Payment status
#     payment_data = {
#         "amount": 1,
#         "payment_date": datetime.datetime.now().strftime('%Y-%m-%d'),
#         "payment_method": "Credit Card",
#         "notes": "Test payment via API"
#     }
#     resp = entry.splose_api_modules.post_payment_to_invoice(
#         base_url = os.environ['splose_api_url'],
#         this_url = os.environ['splose_api_url_list_payments'],
#         secret = os.environ['splose_api_secret'],
#         payment_data = payment_data
#     )
#     assert(isinstance(resp, dict))
#     assert(resp.get('status') == 'Success')

# def test_get_all_awaiting_payment_invoices(entry):
#     patient_to_contact_mapping = entry.splose_api_modules.get_patient_to_contact_mapping()
#     _ = entry.splose_api_modules.get_all_awaiting_payment_invoices(patient_to_contact_mapping)
#     # Check the output - it should be a list
#     assert(isinstance(_, list))
#     # save the result to a csv file for manual inspection
#     now = datetime.datetime.now()
#     filename = f"tests/data/__expected_splose_all_awaiting_payment_invoices_{now.strftime('%Y%m%d_%H%M%S')}"
#     _save_json_result_to_local_csv_file(result=_, filename=filename, sample_rows=99999)

# def test_get_patient_to_contact_mapping(entry):
#     _ = entry.splose_api_modules.get_patient_to_contact_mapping()
#     # Check the output - it should be a dict
#     assert(isinstance(_, dict))
#     assert(len(_) > 0)
#     # save the result to a pretty formatted json file for manual inspection
#     now = datetime.datetime.now()
#     filename = f"tests/data/__expected_splose_patient_to_contact_mapping_{now.strftime('%Y%m%d_%H%M%S')}.json"
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(_, f, ensure_ascii=False, indent=4)

# def test_filter_for_invoices(entry):
#     patient_to_contact_mapping = entry.splose_api_modules.get_patient_to_contact_mapping()
#     _ = entry.splose_api_modules.get_all_awaiting_payment_invoices(patient_to_contact_mapping)
#     filter_invoice_id_list = [7420789, 7421320, 7421290, 7421285, 7421277]
#     filtered_invoices = entry.splose_api_modules.filter_for_invoices(_, filter_invoice_id_list)
#     # Check the output - it should be a list of size 5
#     assert(isinstance(filtered_invoices, list))
#     assert(len(filtered_invoices) >= 2)

# def test_update_invoices_with_payments(entry):
#     patient_to_contact_mapping = entry.splose_api_modules.get_patient_to_contact_mapping()
#     _ = entry.splose_api_modules.get_all_awaiting_payment_invoices(patient_to_contact_mapping)
#     # load the last __pytest_to_load_myob_payments_after_ file from tests/data/ to a dict testing_payment_dict
#     testing_payment_dict = {}
#     filename_to_load = 'placeholder.json'
#     for file in os.listdir('tests/data/'):
#         if file.startswith('__pytest_to_load_myob_payments_after_') and file.endswith('.json'):
#             filename_to_load = os.path.join('tests/data/', file)
#             # break after finding the first match
#             break
#     with open(filename_to_load, 'r', encoding='utf-8') as f:
#         testing_payment_dict = json.load(f)
#     assert(
#         isinstance(testing_payment_dict, dict)
#     )
    
#     # Now update these invoices with payments of $1 each
#     updated_invoices = entry.splose_api_modules.update_invoices_with_payments(
#         invoice_list = _,
#         payment_dict = testing_payment_dict
#     )
#     # Check the output - it should be a list of size 5
#     assert(isinstance(updated_invoices, list))
#     assert(len(updated_invoices) >= 0)

# def test_update_invoices_with_payment_gaps(entry):
#     patient_to_contact_mapping = entry.splose_api_modules.get_patient_to_contact_mapping()
#     _ = entry.splose_api_modules.get_all_awaiting_payment_invoices(patient_to_contact_mapping)
#     # load the last __pytest_to_load_myob_payments_after_ file from tests/data/ to a dict testing_payment_dict
#     testing_payment_dict = {}
#     filename_to_load = 'placeholder.json'
#     for file in os.listdir('tests/data/'):
#         if file.startswith('__pytest_to_load_myob_payments_after_') and file.endswith('.json'):
#             filename_to_load = os.path.join('tests/data/', file)
#             # break after finding the first match
#             break
#     with open(filename_to_load, 'r', encoding='utf-8') as f:
#         testing_payment_dict = json.load(f)
#     assert(
#         isinstance(testing_payment_dict, dict)
#     )
    
#     # Now update these invoices with payments of $1 each
#     updated_invoices = entry.splose_api_modules.update_invoices_with_payment_gaps(
#         invoice_list = _,
#         payment_dict = testing_payment_dict
#     )
#     # Check the output - it should be a list of size 5
#     assert(isinstance(updated_invoices, list))
#     assert(len(updated_invoices) >= 0)

# def test_example_case(entry):
#     """ This example shows how test case works. """
#     # Construct a mock HTTP request.
#     req = func.HttpRequest(method='GET',
#                            body=None,
#                            url='/api/func_http_trigger',
#                            params={'value': '21'})
#     # Call the function.
#     func_call = entry.func_http_trigger.build().get_user_function()
#     resp = func_call(req)
#     # Check the output.
#     assert(
#         resp.get_body() == b'21 * 2 = 42'
#     )

# def test_func_alayacare_billable_item(entry):
#     """ This test case checks for total billable item count 2025-04-01 to 2025-05-01. """
#     # Construct a mock HTTP request.
#     req = func.HttpRequest(method='GET',
#                            body=None,
#                            url='/api/func_alayacare_billable_item',
#                            params={
#                                'start_date': '2025-01-01T00:00:00Z', 
#                                'end_date': '2025-02-01T00:00:00Z',
#                                'include': 'invoices',
#                                'include': 'master_invoice',
#                                'include': 'taxes',
#                                'include': 'employee'
#                            })
#     # Call the function.
#     func_call = entry.func_alayacare_billable_item.build().get_user_function()
#     resp = func_call(req)
#     # Check the output.
#     expected_response = b'{"ingestion": [{"page": 1, "expected_size": 10000, "ac_status_code": 200, "ac_message": "Retrieved 10000 billable items from page 1.", "ac_record_count": 10000, "sf_status": "success", "sf_message": "Successfully inserted 10000 rows into table alayacare_billable_item", "sf_record_count": 10000}, {"page": 2, "expected_size": 10000, "ac_status_code": 200, "ac_message": "Retrieved 10000 billable items from page 2.", "ac_record_count": 10000, "sf_status": "success", "sf_message": "Successfully inserted 10000 rows into table alayacare_billable_item", "sf_record_count": 10000}, {"page": 3, "expected_size": 10000, "ac_status_code": 200, "ac_message": "Retrieved 10000 billable items from page 3.", "ac_record_count": 10000, "sf_status": "success", "sf_message": "Successfully inserted 10000 rows into table alayacare_billable_item", "sf_record_count": 10000}, {"page": 4, "expected_size": 8062, "ac_status_code": 200, "ac_message": "Retrieved 8062 billable items from page 4.", "ac_record_count": 8062, "sf_status": "success", "sf_message": "Successfully inserted 8062 rows into table alayacare_billable_item", "sf_record_count": 8062}], "snowflake_curation_procedure": {"message": "records updated into curation layer table", "status": "success", "total_records_curated": '
#     assert(
#         resp.status_code == 200
#     )
#     assert(
#         resp.get_body().startswith(expected_response)
#     )
