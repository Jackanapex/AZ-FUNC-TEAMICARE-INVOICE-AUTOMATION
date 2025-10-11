import azure.functions as func
import logging
import os
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn
from test_utils import _save_json_result_to_local_csv_file


def test_func_salesforce_dimple_export_session__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_session__c.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2018-01-01T00:00:00Z and LastModifiedDate < 2018-04-11T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Session__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))
    
def test_func_salesforce_dimple_export_sked__job__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_sked__job__c.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "sked__Job__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_account(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_account.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Account", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_contact(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_contact.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Contact", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_sked__availability__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_sked__availability__c.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "sked__Availability__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_sked__resource__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_sked__resource__c.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "sked__Resource__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_user(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_user.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "User", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_patient__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_patient__c.build().get_user_function()
    req = MockIn('LastModifiedDate = LAST_N_DAYS:19')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Patient__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_dimple_export_sked__region__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_export_sked__region__c.build().get_user_function()
    req = MockIn('LastModifiedDate >= 2018-01-01T00:00:00Z AND LastModifiedDate < 2024-11-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "sked__Region__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Dimple'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_plena_export_account(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_plena_export_account.build().get_user_function()
    # test when record is not available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2020-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    assert(queuestr.val.startswith('No record - Salesforce Plena'))
    assert(outblobstr.val is None)
    # test when record is available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2025-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Account", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Plena Account -'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_plena_export_claro_accommodation__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_plena_export_claro_accommodation__c.build().get_user_function()
    # test when record is not available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2020-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    assert(queuestr.val.startswith('No record - Salesforce Plena'))
    assert(outblobstr.val is None)
    # test when record is available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2025-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Claro_Accommodation__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Plena Claro_Accommodation__c -'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_plena_export_bed__c(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_plena_export_bed__c.build().get_user_function()
    # test when record is not available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2020-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    assert(queuestr.val.startswith('No record - Salesforce Plena'))
    assert(outblobstr.val is None)
    # test when record is available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2025-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Bed__c", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Plena Bed__c -'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_plena_export_opportunity(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_plena_export_opportunity.build().get_user_function()
    # test when record is not available
    req = MockIn('LastModifiedDate >= 2020-01-01T00:00:00Z AND LastModifiedDate < 2020-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    blobinstr = None
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    assert(queuestr.val.startswith('No record - Salesforce Plena'))
    assert(outblobstr.val is None)
    # test when record is available
    req = MockIn('LastModifiedDate >= 2024-01-01T00:00:00Z AND LastModifiedDate < 2024-04-10T00:00:00Z')
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobinstr, req, outblobstr, queuestr)                                                                              
    # Check the output.
    expected_start = '[{"attributes": {"type": "Opportunity", "url": '
    assert(queuestr.val.startswith('done: True - Salesforce Plena'))
    assert(outblobstr.val.startswith(expected_start))

def test_func_salesforce_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_main.build().get_user_function()
    req = MockTimer()
    queuestr = MockOut()
    blobstr = MockOut()
    blobinstr = '2020-01-01T00:00:00Z'
    _ = func_call(req, blobstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr,
                  queuestr, blobinstr, blobstr)
    # Check the output.
    assert(queuestr.val)
    assert(blobstr.val)

def test_get_session_and_instance(entry):
    """ This example shows how test case works. """
    # refresh plena session
    plena_session = entry.salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
    plena_session_id, plena_instance = plena_session.renew_session()
    logging.info(f'plena_session_id: {plena_session_id}')
    logging.info(f'plena_instance: {plena_instance}')
    # refresh dimple session
    dimple_session = entry.salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
    dimple_session_id, dimple_instance = dimple_session.renew_session()
    logging.info(f'dimple_session_id: {dimple_session_id}')
    logging.info(f'dimple_instance: {dimple_instance}')                                                                        
    # Check the output.
    assert(plena_session_id)
    assert(plena_instance)
    assert(dimple_session_id)
    assert(dimple_instance)

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