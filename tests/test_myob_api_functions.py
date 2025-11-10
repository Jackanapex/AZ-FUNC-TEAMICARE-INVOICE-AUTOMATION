import azure.functions as func
import os
import datetime
import logging
import random
import string
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn
from test_utils import _save_json_result_to_local_csv_file

def test_func_myob_authorize(entry):
    """ This example shows how test case works. """
    # Call the function.
    # func_call = entry.func_myob_authorize()
    inblobstr = os.environ.get("myob_pytest_refresh_token","")
    outblobstr_0 = MockOut()
    outblobstr_1 = MockOut()
    _ = entry.func_myob_authorize(inblobstr, outblobstr_0, outblobstr_1)                                                                              
    # Check the output.
    assert(len(outblobstr_0.val) > 0)
    assert(len(outblobstr_1.val) > 0)

def test_func_get_new_refresh_token(entry):
    """ This example shows how test case works. """
    # Construct a mock HTTP request.
    code = os.environ.get("myob_pytest_code","")
    business_id = os.environ.get("myob_pytest_business_id","")
    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/func_get_new_refresh_token',
                           params={'code': code, 'businessId': business_id})
    # Call the function.
    func_call = entry.func_get_new_refresh_token.build().get_user_function()
    outblobstr_0 = MockOut()
    outblobstr_1 = MockOut()
    outblobstr_2 = MockOut()
    resp = func_call(req, outblobstr_0, outblobstr_1, outblobstr_2)
    # Check the output.
    assert(
        isinstance(resp, dict)
    )

def test_func_myob_get_company_info(entry):
    """ This example shows how test case works. """
    # Construct a mock HTTP request.
    access_token = os.environ.get("myob_pytest_access_token","")
    refresh_token = os.environ.get("myob_pytest_refresh_token","")
    outblobstr_0 = MockOut()
    outblobstr_1 = MockOut()
    # Call the function.
    resp = entry.func_myob_get_company_info(access_token, refresh_token, outblobstr_0, outblobstr_1)
    # Check the output.
    assert(
        isinstance(resp, dict)
    )

def test_get_contact_customer(entry):
    ''' This shows how test case works. '''
    access_token = os.environ.get("myob_pytest_access_token","")
    business_id = os.environ.get("myob_pytest_business_id","")
    display_id = "SPL_P_3913081"
    resp = entry.myob_api_modules.get_contact_customer(access_token, business_id, display_id)
    assert(
        resp.get("Items", [{}])[0].get("DisplayID","") == display_id
    )

def test_post_and_delete_contact_customer(entry):
    ''' This shows how test case works. '''
    access_token = os.environ.get("myob_pytest_access_token","")
    business_id = os.environ.get("myob_pytest_business_id","")
    # create a random DisplayID
    random_display_id = "TEST_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    logging.info(f"Generated random DisplayID for test customer: {random_display_id}")
    customer_data = {
        "LastName": "temp_test_lastname",
        "FirstName": "temp_test_firstname",
        "IsIndividual": True,
        "DisplayID": random_display_id,
        "SellingDetails": {
            "TaxCode": {
                "UID": os.environ.get("myob_gst_tax_uid","")
            },
            "FreightTaxCode": {
                "UID": os.environ.get("myob_gst_tax_uid","")
            }
        }
    }
    # Post the new customer
    post_resp = entry.myob_api_modules.post_contact_customer(access_token, business_id, customer_data)
    assert(
        post_resp
    )
    # Get the customer to verify it was created
    get_resp = entry.myob_api_modules.get_contact_customer(access_token, business_id, random_display_id)
    assert(
        get_resp.get("Items", [{}])[0].get("DisplayID","") == random_display_id
    )
    test_customer_uid = get_resp.get("Items", [{}])[0].get("UID","")
    # Now delete the customer
    delete_resp = entry.myob_api_modules.delete_contact_customer(access_token, business_id, test_customer_uid)
    assert(
        delete_resp
    )

def test_post_a_contact_customer_without_display_id_and_clean_off(entry):
    ''' This shows how test case works. '''
    access_token = os.environ.get("myob_pytest_access_token","")
    business_id = os.environ.get("myob_pytest_business_id","")
    customer_data = {
        "LastName": "temp_lastname",
        "FirstName": "temp_firstname",
        "IsIndividual": True,
        "SellingDetails": {
            "TaxCode": {
                "UID": os.environ.get("myob_gst_tax_uid","")
            },
            "FreightTaxCode": {
                "UID": os.environ.get("myob_gst_tax_uid","")
            }
        }
    }
    # Post the new customer
    post_resp = entry.myob_api_modules.post_contact_customer(access_token, business_id, customer_data)
    assert(
        post_resp
    )
    # now delete all customers without DisplayID
    delete_resp = entry.myob_api_modules.delete_contact_customers_without_display_id(access_token, business_id)
    assert(
        isinstance(delete_resp, list)
    )
    assert(
        len(delete_resp) > 0
    )
        