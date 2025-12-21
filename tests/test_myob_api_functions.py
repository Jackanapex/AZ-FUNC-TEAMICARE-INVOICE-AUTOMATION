import azure.functions as func
import os
import datetime
import logging
import random
import string
import json
import base64
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn
from test_utils import MockBlobClient
from test_utils import _save_json_result_to_local_csv_file

def test_func_myob_authorize(entry):
    """ This example shows how test case works. """
    # Call the function.
    # func_call = entry.func_myob_authorize()
    inblobstr = os.environ.get("myob_pytest_refresh_token","")
    outblobstr_0 = MockOut()
    outblobstr_1 = MockOut()
    queuestr = MockOut()
    _ = entry.func_myob_authorize(inblobstr, outblobstr_0, outblobstr_1, queuestr)                                                                              
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
    queuestr = MockOut()
    # Call the function.
    resp = entry.func_myob_get_company_info(access_token, refresh_token, outblobstr_0, outblobstr_1, queuestr)
    # Check the output.
    assert(
        isinstance(resp, dict)
    )

def test_func_filter_splose_invoice_for_myob_import(entry):
    """ This example shows how test case works. """
    # Construct a mock Timer request.
    func_call = entry.func_filter_splose_invoice_for_myob_import.build().get_user_function()
    myTimer = MockTimer()
    inputblobBusinessId = os.environ.get("myob_pytest_business_id","")
    inputblobAccessToken = os.environ.get("myob_pytest_access_token","")
    inputblobRefreshToken = os.environ.get("myob_pytest_refresh_token","")
    outputblobAccessToken = MockOut()
    outputblobRefreshToken = MockOut()
    queuestr = MockOut()
    # Call the function.
    resp = func_call(
        myTimer,
        inputblobBusinessId,
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken,
        queuestr
    )
    # Check if function runs without error
    assert(
        resp is None
    )

def test_func_convert_splose_invoices_to_myob_customers(entry):
    """ This example shows how test case works. """
    # Construct a mock blob trigger request.
    func_call = entry.func_convert_splose_invoices_to_myob_customers.build().get_user_function()
    base64_string_utf8 = r"WwogICAgewogICAgICAgICJpZCI6IDEyMTQyODQ0LAogICAgICAgICJpbnZvaWNlTnVtYmVyIjogIlBTTU45OTk5IiwKICAgICAgICAiaXNzdWVEYXRlIjogIjIwMjUtMTItMDdUMTM6MDA6MDAuMDAwWiIsCiAgICAgICAgImR1ZURhdGUiOiAiMjAyNS0xMi0xNVQxMjo1OTo1OS4wMDBaIiwKICAgICAgICAicGF0aWVudElkIjogMzkzNjQ1OSwKICAgICAgICAiY29udGFjdElkIjogIlRFU1Q5OTkiLAogICAgICAgICJsb2NhdGlvbklkIjogOTIzNCwKICAgICAgICAicHJhY3RpdGlvbmVySWQiOiAzNzY3NiwKICAgICAgICAiZXh0cmFCaWxsaW5nSW5mbyI6IG51bGwsCiAgICAgICAgInN1YnRvdGFsIjogNjk4Ljc4LAogICAgICAgICJ0YXhTdGF0dXMiOiAiZXhjbHVkaW5nIiwKICAgICAgICAidGF4IjogMCwKICAgICAgICAidG90YWwiOiA2OTguNzgsCiAgICAgICAgInBhaWRBbW91bnQiOiAwLjAsCiAgICAgICAgInN0YXR1cyI6ICJBd2FpdGluZyBQYXltZW50IiwKICAgICAgICAiaW52b2ljZUl0ZW1zIjogWwogICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAiaWQiOiAyMzcwMzg2MiwKICAgICAgICAgICAgICAgICJ0eXBlIjogImFwcG9pbnRtZW50IiwKICAgICAgICAgICAgICAgICJ0eXBlSWQiOiA4NTExMjIzOCwKICAgICAgICAgICAgICAgICJjb2RlIjogIjE1XzYxN18wMTI4XzFfMyIsCiAgICAgICAgICAgICAgICAiZGVzY3JpcHRpb24iOiAiMTcgTm92IDIwMjUsIDA0OjAwcG0gLSBORElTIC0gQXNzZXNzbWVudCBSZWNvbW1lbmRhdGlvbiBUaGVyYXB5IG9yIFRyYWluaW5nIC0gT2NjdXBhdGlvbmFsIFRoZXJhcGlzdHMgKE5ESVMgT1QpIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAxOTMuOTksCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAxLAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODYzLAogICAgICAgICAgICAgICAgInR5cGUiOiAic3VwcG9ydEl0ZW0iLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDEzMzYxMzA0LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNjE3XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICIxNyBOb3YgMjAyNSwgUHJvdmlkZXIgVHJhdmVsIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiA5NywKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDEsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjQsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJzdXBwb3J0SXRlbSIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogMTM0NDEzMjcsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV83OTlfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIjE3IE5vdiAyMDI1LCBQcm92aWRlciBUcmF2ZWwgLSBOb24tTGFib3VyIENvc3RzIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAwLjk5LAogICAgICAgICAgICAgICAgInF1YW50aXR5IjogMTAsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjUsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJhcHBvaW50bWVudCIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogODUxMTIyOTEsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIk1vbiAxNyBOb3YgMjAyNSwgMDU6MDBwbSAtIE5vbi1GYWNlLXRvLUZhY2UgU3VwcG9ydCBQcm92aXNpb24gKE5ESVMgT1QpIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAxOTMuOTksCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAwLjI1LAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODY2LAogICAgICAgICAgICAgICAgInR5cGUiOiAiYXBwb2ludG1lbnQiLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDg3NjE3ODg1LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNjE3XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICJNb24gMSBEZWMgMjAyNSwgMDQ6MDBwbSAtIE5ESVMgLSBBc3Nlc3NtZW50IFJlY29tbWVuZGF0aW9uIFRoZXJhcHkgb3IgVHJhaW5pbmcgLSBPY2N1cGF0aW9uYWwgVGhlcmFwaXN0cyAoTkRJUyBPVCkiLAogICAgICAgICAgICAgICAgInVuaXRQcmljZSI6IDE5My45OSwKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDEsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjcsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJzdXBwb3J0SXRlbSIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogMTQxOTg5NzgsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIjEgRGVjIDIwMjUsIFByb3ZpZGVyIFRyYXZlbCIsCiAgICAgICAgICAgICAgICAidW5pdFByaWNlIjogOTcsCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAxLAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODY4LAogICAgICAgICAgICAgICAgInR5cGUiOiAic3VwcG9ydEl0ZW0iLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDE0MTk4OTc5LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNzk5XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICIxIERlYyAyMDI1LCBQcm92aWRlciBUcmF2ZWwgLSBOb24tTGFib3VyIENvc3RzIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAwLjk5LAogICAgICAgICAgICAgICAgInF1YW50aXR5IjogMTAsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjksCiAgICAgICAgICAgICAgICAidHlwZSI6ICJhcHBvaW50bWVudCIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogODg2Mjc3MjksCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIk1vbiAxIERlYyAyMDI1LCAwNTowMHBtIC0gTm9uLUZhY2UtdG8tRmFjZSBTdXBwb3J0IFByb3Zpc2lvbiAoTkRJUyBPVCkiLAogICAgICAgICAgICAgICAgInVuaXRQcmljZSI6IDE5My45OSwKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDAuMjUsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfQogICAgICAgIF0sCiAgICAgICAgInBheW1lbnRJZHMiOiBbXSwKICAgICAgICAicmVmZXJlbmNlTnVtYmVycyI6IFtdLAogICAgICAgICJpc0FyY2hpdmVkIjogZmFsc2UsCiAgICAgICAgInJlZmVyZW5jZSI6ICJOVEhTMjUxMjAxMDEiLAogICAgICAgICJkZXNjcmlwdGlvbiI6ICJQYXltZW50IE1ldGhvZHM6XG5CYW5rIFRyYW5zZmVyc1xuQWNjb3VudCBOYW1lOiBUZWFtaUNhcmUgUHR5IEx0ZCBcbkJTQjogMDEzLTQwMlxuQWNjb3VudCAjOiAxNjIzNzY1ODhcblJlZmVyZW5jZSAjTlRIUzI1MTIwMTAxIiwKICAgICAgICAiY3JlYXRlZEF0IjogIjIwMjUtMTItMDhUMDg6MDQ6MzYuMDAwWiIsCiAgICAgICAgInVwZGF0ZWRBdCI6ICIyMDI1LTEyLTA4VDA4OjExOjQ5LjAwMFoiLAogICAgICAgICJjb250YWN0X25hbWUiOiAiV2F5YSBQbGFuIE1hbmFnZXJzIiwKICAgICAgICAiY29udGFjdF9jb21wYW55TmFtZSI6ICJXYXlhIFBsYW4gTWFuYWdlcnMiLAogICAgICAgICJjb250YWN0X2VtYWlsIjogInBtQHdheWFwbS5jb20uYXUiLAogICAgICAgICJjb250YWN0X3Bob25lTnVtYmVycyI6IFtdLAogICAgICAgICJjb250YWN0X2FkZHJlc3NMMSI6IG51bGwsCiAgICAgICAgImNvbnRhY3RfYWRkcmVzc0wyIjogbnVsbCwKICAgICAgICAiY29udGFjdF9hZGRyZXNzTDMiOiBudWxsLAogICAgICAgICJjb250YWN0X3N1YnVyYiI6IG51bGwsCiAgICAgICAgImNvbnRhY3Rfc3RhdGUiOiBudWxsLAogICAgICAgICJjb250YWN0X3Bvc3RhbENvZGUiOiBudWxsLAogICAgICAgICJjb250YWN0X2NvdW50cnkiOiAiQXVzdHJhbGlhIiwKICAgICAgICAicGF0aWVudF9maXJzdG5hbWUiOiAiSmV0dCIsCiAgICAgICAgInBhdGllbnRfbGFzdG5hbWUiOiAiRGF2aXMgU2FjY28iLAogICAgICAgICJwYXRpZW50X3ByZWZlcnJlZE5hbWUiOiAiSmV0dCIsCiAgICAgICAgInBhdGllbnRfZW1haWwiOiBudWxsLAogICAgICAgICJwYXRpZW50X3Bob25lTnVtYmVycyI6IFsKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgInR5cGUiOiAiTW9iaWxlIiwKICAgICAgICAgICAgICAgICJjb2RlIjogIis2MSIsCiAgICAgICAgICAgICAgICAicGhvbmVOdW1iZXIiOiAiMDQzMTIzMzE3NyIKICAgICAgICAgICAgfQogICAgICAgIF0sCiAgICAgICAgInBhdGllbnRfYWRkcmVzc0wxIjogIjEzIFNoZXJicm9va2UgQXZlLCBPYWtsZWlnaCBTb3V0aCBWSUMgMzE2NyIsCiAgICAgICAgInBhdGllbnRfYWRkcmVzc0wyIjogbnVsbCwKICAgICAgICAicGF0aWVudF9hZGRyZXNzTDMiOiBudWxsLAogICAgICAgICJwYXRpZW50X2NpdHkiOiAiT2FrbGVpZ2ggU291dGggVklDIDMxNjciLAogICAgICAgICJwYXRpZW50X3N0YXRlIjogIlZJQyIsCiAgICAgICAgInBhdGllbnRfcG9zdGFsQ29kZSI6ICIzMTY3IiwKICAgICAgICAicGF0aWVudF9jb3VudHJ5IjogIkF1c3RyYWxpYSIsCiAgICAgICAgInBhdGllbnRfbmRpc051bWJlciI6ICI0MzExMTEyNDIiLAogICAgICAgICJwYXRpZW50X25kaXNJbmZvIjogbnVsbCwKICAgICAgICAicGF0aWVudF9iaXJ0aGRhdGUiOiAiMjAxMS0xMC0xOFQwMDowMDowMC4wMDBaIiwKICAgICAgICAicHJhY3RpdGlvbmVyX2ZpcnN0bmFtZSI6ICJSaWNoYXJkIiwKICAgICAgICAicHJhY3RpdGlvbmVyX2xhc3RuYW1lIjogIkNoZW4iLAogICAgICAgICJwcmFjdGl0aW9uZXJfcHJvdmlkZXJOdW1iZXJzIjogW10sCiAgICAgICAgImNvbnRhY3RfZGlzcGxheV9pZCI6ICJTUExfQ19URVNUOTk5IiwKICAgICAgICAiY29udGFjdF9uZGlzX251bWJlciI6IG51bGwsCiAgICAgICAgImNvbnRhY3RfbmRpc19ub21pbmVlX25hbWUiOiBudWxsLAogICAgICAgICJpbnZvaWNlX3R5cGUiOiAiTkRJUyIKICAgIH0KXQ=="
    decoded_string = base64.b64decode(base64_string_utf8).decode('utf-8')
    client = MockBlobClient(decoded_string)
    inputblobBusinessId = os.environ.get("myob_pytest_business_id","")
    inputblobAccessToken = os.environ.get("myob_pytest_access_token","")
    inputblobRefreshToken = os.environ.get("myob_pytest_refresh_token","")
    outputblobAccessToken = MockOut()
    outputblobRefreshToken = MockOut()
    outputblobMyobUpsertedCustomers = MockOut()
    queuestr = MockOut()
    # Call the function.
    resp = func_call(
        client,
        inputblobBusinessId,
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken,
        outputblobMyobUpsertedCustomers,
        queuestr
    )
    # Check the output.
    assert(
        isinstance(json.loads(outputblobMyobUpsertedCustomers.val), dict)
    )
    assert(
        resp is None
    )

def test_func_import_splose_invoices_to_myob(entry):
    """ This example shows how test case works. """
    # Construct a mock blob trigger request.
    func_call = entry.func_import_splose_invoices_to_myob.build().get_user_function()
    base64_string_utf8 = r"WwogICAgewogICAgICAgICJpZCI6IDEyMTQyODQ0LAogICAgICAgICJpbnZvaWNlTnVtYmVyIjogIlBTTU45OTk5IiwKICAgICAgICAiaXNzdWVEYXRlIjogIjIwMjUtMTItMDdUMTM6MDA6MDAuMDAwWiIsCiAgICAgICAgImR1ZURhdGUiOiAiMjAyNS0xMi0xNVQxMjo1OTo1OS4wMDBaIiwKICAgICAgICAicGF0aWVudElkIjogMzkzNjQ1OSwKICAgICAgICAiY29udGFjdElkIjogIlRFU1Q5OTkiLAogICAgICAgICJsb2NhdGlvbklkIjogOTIzNCwKICAgICAgICAicHJhY3RpdGlvbmVySWQiOiAzNzY3NiwKICAgICAgICAiZXh0cmFCaWxsaW5nSW5mbyI6IG51bGwsCiAgICAgICAgInN1YnRvdGFsIjogNjk4Ljc4LAogICAgICAgICJ0YXhTdGF0dXMiOiAiZXhjbHVkaW5nIiwKICAgICAgICAidGF4IjogMCwKICAgICAgICAidG90YWwiOiA2OTguNzgsCiAgICAgICAgInBhaWRBbW91bnQiOiAwLjAsCiAgICAgICAgInN0YXR1cyI6ICJBd2FpdGluZyBQYXltZW50IiwKICAgICAgICAiaW52b2ljZUl0ZW1zIjogWwogICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAiaWQiOiAyMzcwMzg2MiwKICAgICAgICAgICAgICAgICJ0eXBlIjogImFwcG9pbnRtZW50IiwKICAgICAgICAgICAgICAgICJ0eXBlSWQiOiA4NTExMjIzOCwKICAgICAgICAgICAgICAgICJjb2RlIjogIjE1XzYxN18wMTI4XzFfMyIsCiAgICAgICAgICAgICAgICAiZGVzY3JpcHRpb24iOiAiMTcgTm92IDIwMjUsIDA0OjAwcG0gLSBORElTIC0gQXNzZXNzbWVudCBSZWNvbW1lbmRhdGlvbiBUaGVyYXB5IG9yIFRyYWluaW5nIC0gT2NjdXBhdGlvbmFsIFRoZXJhcGlzdHMgKE5ESVMgT1QpIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAxOTMuOTksCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAxLAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODYzLAogICAgICAgICAgICAgICAgInR5cGUiOiAic3VwcG9ydEl0ZW0iLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDEzMzYxMzA0LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNjE3XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICIxNyBOb3YgMjAyNSwgUHJvdmlkZXIgVHJhdmVsIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiA5NywKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDEsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjQsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJzdXBwb3J0SXRlbSIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogMTM0NDEzMjcsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV83OTlfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIjE3IE5vdiAyMDI1LCBQcm92aWRlciBUcmF2ZWwgLSBOb24tTGFib3VyIENvc3RzIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAwLjk5LAogICAgICAgICAgICAgICAgInF1YW50aXR5IjogMTAsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjUsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJhcHBvaW50bWVudCIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogODUxMTIyOTEsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIk1vbiAxNyBOb3YgMjAyNSwgMDU6MDBwbSAtIE5vbi1GYWNlLXRvLUZhY2UgU3VwcG9ydCBQcm92aXNpb24gKE5ESVMgT1QpIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAxOTMuOTksCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAwLjI1LAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODY2LAogICAgICAgICAgICAgICAgInR5cGUiOiAiYXBwb2ludG1lbnQiLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDg3NjE3ODg1LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNjE3XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICJNb24gMSBEZWMgMjAyNSwgMDQ6MDBwbSAtIE5ESVMgLSBBc3Nlc3NtZW50IFJlY29tbWVuZGF0aW9uIFRoZXJhcHkgb3IgVHJhaW5pbmcgLSBPY2N1cGF0aW9uYWwgVGhlcmFwaXN0cyAoTkRJUyBPVCkiLAogICAgICAgICAgICAgICAgInVuaXRQcmljZSI6IDE5My45OSwKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDEsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjcsCiAgICAgICAgICAgICAgICAidHlwZSI6ICJzdXBwb3J0SXRlbSIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogMTQxOTg5NzgsCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIjEgRGVjIDIwMjUsIFByb3ZpZGVyIFRyYXZlbCIsCiAgICAgICAgICAgICAgICAidW5pdFByaWNlIjogOTcsCiAgICAgICAgICAgICAgICAicXVhbnRpdHkiOiAxLAogICAgICAgICAgICAgICAgImRpc2NvdW50IjogbnVsbCwKICAgICAgICAgICAgICAgICJ0YXhUeXBlIjogIlpFUk8iLAogICAgICAgICAgICAgICAgInRheFJhdGUiOiAwCiAgICAgICAgICAgIH0sCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpZCI6IDIzNzAzODY4LAogICAgICAgICAgICAgICAgInR5cGUiOiAic3VwcG9ydEl0ZW0iLAogICAgICAgICAgICAgICAgInR5cGVJZCI6IDE0MTk4OTc5LAogICAgICAgICAgICAgICAgImNvZGUiOiAiMTVfNzk5XzAxMjhfMV8zIiwKICAgICAgICAgICAgICAgICJkZXNjcmlwdGlvbiI6ICIxIERlYyAyMDI1LCBQcm92aWRlciBUcmF2ZWwgLSBOb24tTGFib3VyIENvc3RzIiwKICAgICAgICAgICAgICAgICJ1bml0UHJpY2UiOiAwLjk5LAogICAgICAgICAgICAgICAgInF1YW50aXR5IjogMTAsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfSwKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgImlkIjogMjM3MDM4NjksCiAgICAgICAgICAgICAgICAidHlwZSI6ICJhcHBvaW50bWVudCIsCiAgICAgICAgICAgICAgICAidHlwZUlkIjogODg2Mjc3MjksCiAgICAgICAgICAgICAgICAiY29kZSI6ICIxNV82MTdfMDEyOF8xXzMiLAogICAgICAgICAgICAgICAgImRlc2NyaXB0aW9uIjogIk1vbiAxIERlYyAyMDI1LCAwNTowMHBtIC0gTm9uLUZhY2UtdG8tRmFjZSBTdXBwb3J0IFByb3Zpc2lvbiAoTkRJUyBPVCkiLAogICAgICAgICAgICAgICAgInVuaXRQcmljZSI6IDE5My45OSwKICAgICAgICAgICAgICAgICJxdWFudGl0eSI6IDAuMjUsCiAgICAgICAgICAgICAgICAiZGlzY291bnQiOiBudWxsLAogICAgICAgICAgICAgICAgInRheFR5cGUiOiAiWkVSTyIsCiAgICAgICAgICAgICAgICAidGF4UmF0ZSI6IDAKICAgICAgICAgICAgfQogICAgICAgIF0sCiAgICAgICAgInBheW1lbnRJZHMiOiBbXSwKICAgICAgICAicmVmZXJlbmNlTnVtYmVycyI6IFtdLAogICAgICAgICJpc0FyY2hpdmVkIjogZmFsc2UsCiAgICAgICAgInJlZmVyZW5jZSI6ICJOVEhTMjUxMjAxMDEiLAogICAgICAgICJkZXNjcmlwdGlvbiI6ICJQYXltZW50IE1ldGhvZHM6XG5CYW5rIFRyYW5zZmVyc1xuQWNjb3VudCBOYW1lOiBUZWFtaUNhcmUgUHR5IEx0ZCBcbkJTQjogMDEzLTQwMlxuQWNjb3VudCAjOiAxNjIzNzY1ODhcblJlZmVyZW5jZSAjTlRIUzI1MTIwMTAxIiwKICAgICAgICAiY3JlYXRlZEF0IjogIjIwMjUtMTItMDhUMDg6MDQ6MzYuMDAwWiIsCiAgICAgICAgInVwZGF0ZWRBdCI6ICIyMDI1LTEyLTA4VDA4OjExOjQ5LjAwMFoiLAogICAgICAgICJjb250YWN0X25hbWUiOiAiV2F5YSBQbGFuIE1hbmFnZXJzIiwKICAgICAgICAiY29udGFjdF9jb21wYW55TmFtZSI6ICJXYXlhIFBsYW4gTWFuYWdlcnMiLAogICAgICAgICJjb250YWN0X2VtYWlsIjogInBtQHdheWFwbS5jb20uYXUiLAogICAgICAgICJjb250YWN0X3Bob25lTnVtYmVycyI6IFtdLAogICAgICAgICJjb250YWN0X2FkZHJlc3NMMSI6IG51bGwsCiAgICAgICAgImNvbnRhY3RfYWRkcmVzc0wyIjogbnVsbCwKICAgICAgICAiY29udGFjdF9hZGRyZXNzTDMiOiBudWxsLAogICAgICAgICJjb250YWN0X3N1YnVyYiI6IG51bGwsCiAgICAgICAgImNvbnRhY3Rfc3RhdGUiOiBudWxsLAogICAgICAgICJjb250YWN0X3Bvc3RhbENvZGUiOiBudWxsLAogICAgICAgICJjb250YWN0X2NvdW50cnkiOiAiQXVzdHJhbGlhIiwKICAgICAgICAicGF0aWVudF9maXJzdG5hbWUiOiAiSmV0dCIsCiAgICAgICAgInBhdGllbnRfbGFzdG5hbWUiOiAiRGF2aXMgU2FjY28iLAogICAgICAgICJwYXRpZW50X3ByZWZlcnJlZE5hbWUiOiAiSmV0dCIsCiAgICAgICAgInBhdGllbnRfZW1haWwiOiBudWxsLAogICAgICAgICJwYXRpZW50X3Bob25lTnVtYmVycyI6IFsKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgInR5cGUiOiAiTW9iaWxlIiwKICAgICAgICAgICAgICAgICJjb2RlIjogIis2MSIsCiAgICAgICAgICAgICAgICAicGhvbmVOdW1iZXIiOiAiMDQzMTIzMzE3NyIKICAgICAgICAgICAgfQogICAgICAgIF0sCiAgICAgICAgInBhdGllbnRfYWRkcmVzc0wxIjogIjEzIFNoZXJicm9va2UgQXZlLCBPYWtsZWlnaCBTb3V0aCBWSUMgMzE2NyIsCiAgICAgICAgInBhdGllbnRfYWRkcmVzc0wyIjogbnVsbCwKICAgICAgICAicGF0aWVudF9hZGRyZXNzTDMiOiBudWxsLAogICAgICAgICJwYXRpZW50X2NpdHkiOiAiT2FrbGVpZ2ggU291dGggVklDIDMxNjciLAogICAgICAgICJwYXRpZW50X3N0YXRlIjogIlZJQyIsCiAgICAgICAgInBhdGllbnRfcG9zdGFsQ29kZSI6ICIzMTY3IiwKICAgICAgICAicGF0aWVudF9jb3VudHJ5IjogIkF1c3RyYWxpYSIsCiAgICAgICAgInBhdGllbnRfbmRpc051bWJlciI6ICI0MzExMTEyNDIiLAogICAgICAgICJwYXRpZW50X25kaXNJbmZvIjogbnVsbCwKICAgICAgICAicGF0aWVudF9iaXJ0aGRhdGUiOiAiMjAxMS0xMC0xOFQwMDowMDowMC4wMDBaIiwKICAgICAgICAicHJhY3RpdGlvbmVyX2ZpcnN0bmFtZSI6ICJSaWNoYXJkIiwKICAgICAgICAicHJhY3RpdGlvbmVyX2xhc3RuYW1lIjogIkNoZW4iLAogICAgICAgICJwcmFjdGl0aW9uZXJfcHJvdmlkZXJOdW1iZXJzIjogW10sCiAgICAgICAgImNvbnRhY3RfZGlzcGxheV9pZCI6ICJTUExfQ19URVNUOTk5IiwKICAgICAgICAiY29udGFjdF9uZGlzX251bWJlciI6IG51bGwsCiAgICAgICAgImNvbnRhY3RfbmRpc19ub21pbmVlX25hbWUiOiBudWxsLAogICAgICAgICJpbnZvaWNlX3R5cGUiOiAiTkRJUyIKICAgIH0KXQ=="
    decoded_string = base64.b64decode(base64_string_utf8).decode('utf-8')
    client = MockBlobClient(decoded_string)
    inputblobBusinessId = os.environ.get("myob_pytest_business_id","")
    base64_string_utf8 = r"ewogICAgIlNQTF9DX1RFU1Q5OTkiOiAiZDI3ZTY0NWItOWViMy00YTc5LTlhYTktYmRjOGRlNTM2ZDcxIgp9"
    decoded_string = base64.b64decode(base64_string_utf8).decode('utf-8')
    inputblobMyobUpsertedCustomers = decoded_string
    inputblobAccessToken = os.environ.get("myob_pytest_access_token","")
    inputblobRefreshToken = os.environ.get("myob_pytest_refresh_token","")
    outputblobAccessToken = MockOut()
    outputblobRefreshToken = MockOut()
    outputblobMyobNewInvoices = MockOut()
    queuestr = MockOut()
    # Call the function.
    resp = func_call(
        client,
        inputblobMyobUpsertedCustomers,
        inputblobBusinessId,
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken,
        outputblobMyobNewInvoices,
        queuestr
    )
    # Check the output.
    assert(
        isinstance(json.loads(outputblobMyobNewInvoices.val), dict)
    )
    # now delete all invoices without Number
    delete_resp = entry.myob_api_modules.delete_sale_invoice_service_without_number(
        outputblobAccessToken.val, inputblobBusinessId
    )
    assert(
        isinstance(delete_resp, list)
    )
    assert(
        len(delete_resp) > 0
    )
    # now delete all customers without DisplayID
    delete_resp = entry.myob_api_modules.delete_contact_customers_without_display_id(
        outputblobAccessToken.val, inputblobBusinessId
    )
    assert(
        isinstance(delete_resp, list)
    )
    assert(
        len(delete_resp) > 0
    )

def test_func_get_customer_payments_after_date_and_convert_to_invoice_key(entry):
    """ This example shows how test case works. """
    # Construct a mock blob trigger request.
    func_call = entry.func_get_customer_payments_after_date_and_convert_to_invoice_key.build().get_user_function()
    myTimer = MockTimer()
    inputblobpage = '2025-11-01T00:00:00Z'
    inputblobBusinessId  = os.environ.get("myob_pytest_business_id","")
    inputblobAccessToken = os.environ.get("myob_pytest_access_token","")
    inputblobRefreshToken = os.environ.get("myob_pytest_refresh_token","")
    outputblobpage = MockOut()
    outputblobAccessToken = MockOut()
    outputblobRefreshToken = MockOut()
    queuestr = MockOut()
    # Call the function.
    resp = func_call(
        myTimer,
        inputblobpage,
        inputblobBusinessId,
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobpage,
        outputblobAccessToken,
        outputblobRefreshToken,
        queuestr
    )
    # Check the output.
    assert(
        resp is None
    )

def test_func_update_splose_invoices_with_payment_gaps(entry):
    """ This example shows how test case works. """
    # Construct a mock blob trigger request.
    func_call = entry.func_update_splose_invoices_with_payment_gaps.build().get_user_function()
    base64_string_utf8 = r"ewogICAgIjI1MTAzMTA0IjogewogICAgICAgICJhbW91bnQiOiAyMjYuOTcsCiAgICAgICAgInBheW1lbnREYXRlIjogIjIwMjUtMTEtMTkiCiAgICB9LAogICAgIjI1MTEyMTAxIjogewogICAgICAgICJhbW91bnQiOiAyMjYuOTcsCiAgICAgICAgInBheW1lbnREYXRlIjogIjIwMjUtMTItMDMiCiAgICB9LAogICAgIjIyMDcyNTA2IjogewogICAgICAgICJhbW91bnQiOiAzMDAuMCwKICAgICAgICAicGF5bWVudERhdGUiOiAiMjAyNS0xMS0wMyIKICAgIH0KfQ=="
    decoded_string = base64.b64decode(base64_string_utf8).decode('utf-8')
    client = MockBlobClient(decoded_string)
    outputblobSploseInvoicesWithPayments = MockOut()
    # Call the function.
    resp = func_call(
        client,
        outputblobSploseInvoicesWithPayments
    )
    # Check the output.
    assert(
        isinstance(json.loads(outputblobSploseInvoicesWithPayments.val), list)
    )

def test_recursively_get_all_item_invoices(entry):
    ''' This shows how test case works. '''
    access_token = os.environ.get("myob_pytest_access_token","")
    business_id = os.environ.get("myob_pytest_business_id","")
    resp = entry.myob_api_modules.recursively_get_all_item_invoices(access_token, business_id)
    assert(
        isinstance(resp, list)
    )
    assert(
        len(resp) > 0
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

def test_post_a_sale_invoice_service_without_number_and_clean_off(entry):
    ''' This shows how test case works. '''
    access_token = os.environ.get("myob_pytest_access_token","")
    business_id = os.environ.get("myob_pytest_business_id","")
    invoice_data = {
        "Number": f"PSMN_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
        "Date": "2025-09-02T00:00:00Z",
        "Customer": {
            "UID": "57255759-f2de-4d57-aca5-285c887dda3e"
        },
        "IsTaxInclusive": True,
        "Lines": [
            {
                "Type": "Transaction",
                "Description": "Postman Sample Update\nNew Line Item\nNew Line Item",
                "Account": {
                    "UID": os.environ.get("myob_service_income_account_uid","")
                },
                "UnitOfMeasure" : "hour",
                "UnitCount" : 2,
                "UnitPrice" : 61.73,
                "Job": None,
                "TaxCode": {
                    "UID": os.environ.get("myob_gstfree_tax_uid","")
                }
            }
        ],
        "Category": {"UID": os.environ.get("myob_category_private_uid","")},
        "Comment": "comment test field",
        "ShippingMethod": None,
        "JournalMemo": "Postman sample service JournalMemo",
        "Order": None
    }
    # Post the new invoice
    post_resp = entry.myob_api_modules.upsert_sale_invoice_service(access_token, business_id, invoice_data)
    assert(
        post_resp
    )
    # now delete all invoices without Number
    delete_resp = entry.myob_api_modules.delete_sale_invoice_service_without_number(access_token, business_id)
    assert(
        isinstance(delete_resp, list)
    )
    assert(
        len(delete_resp) > 0
    )

def test_filter_splose_invoice_for_myob_import(entry):
    splose_patient_to_contact_mapping = entry.splose_api_modules.get_patient_to_contact_mapping()
    _ = entry.splose_api_modules.get_all_awaiting_payment_invoices(splose_patient_to_contact_mapping)
    pending_invoice_number_list = [[str(i['id']), str(i['invoiceNumber'])] for i in _]
    invoice_id_to_import_list = []
    all_myob_invoices = entry.myob_api_modules.recursively_get_all_item_invoices(
        access_token=os.environ.get('myob_pytest_access_token',''),
        business_id=os.environ.get('myob_pytest_business_id','')
    )
    for invoice_number in pending_invoice_number_list:
        if not entry.myob_api_modules.is_sale_invoice_service_existing_in_myob(
            splose_invoice_number=invoice_number[1],
            myob_invoice_list=all_myob_invoices
        ):
            invoice_id_to_import_list.append(int(invoice_number[0]))
    pending_invoices = entry.splose_api_modules.filter_for_invoices(
        invoice_list = _,
        invoice_filter_id_list = invoice_id_to_import_list
    )
    # save the pending invoices to csv file for manual inspection
    now = datetime.datetime.now()
    filename = f"tests/data/__expected_splose_pending_invoices_to_import_{now.strftime('%Y%m%d_%H%M%S')}"
    _save_json_result_to_local_csv_file(result=pending_invoices, filename=filename, sample_rows=99999)
    # also save the pending invoices to a pretty formatted json file for loading to another test later
    now = datetime.datetime.now()
    filename = f"tests/data/__pytest_to_load_splose_pending_invoices_to_import_{now.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(pending_invoices, f, ensure_ascii=False, indent=4)

def test_convert_splose_invoices_to_myob_customers(entry):
    # load the pending invoices from a pretty formatted json file
    pending_invoices = []
    filename_to_load = 'placeholder.json'
    for file in os.listdir('tests/data/'):
        # find the latest file starting with __pytest_to_load_splose_pending_invoices_to_import_
        if file.startswith('__pytest_to_load_splose_pending_invoices_to_import_') and file.endswith('.json'):
            filename_to_load = os.path.join('tests/data/', file)
            # break after finding the first match
            break
    with open(filename_to_load, 'r', encoding='utf-8') as f:
        pending_invoices = json.load(f)
    assert(
        isinstance(pending_invoices, list)
    )
    # convert the pending invoices to myob customers
    result_dict = entry.myob_api_modules.convert_splose_invoice_to_myob_customer(
        access_token=os.environ.get('myob_pytest_access_token',''),
        business_id=os.environ.get('myob_pytest_business_id',''),
        splose_invoice_dict_list=pending_invoices
    )
    assert(
        isinstance(result_dict, dict)
    )
    # save the result to a pretty formatted json file for manual inspection and loading to another test later
    now = datetime.datetime.now()
    filename = f"tests/data/__pytest_to_load_myob_converted_customers_{now.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)

def test_import_splose_invoices_to_myob(entry):
    # load the pending invoices from a pretty formatted json file
    pending_invoices = []
    filename_to_load = 'placeholder.json'
    for file in os.listdir('tests/data/'):
        if file.startswith('__pytest_to_load_splose_pending_invoices_to_import_') and file.endswith('.json'):
            filename_to_load = os.path.join('tests/data/', file)
            # break after finding the first match
            break
    with open(filename_to_load, 'r', encoding='utf-8') as f:
        pending_invoices = json.load(f)
    assert(
        isinstance(pending_invoices, list)
    )
    # load the converted customer mapping from a pretty formatted json file
    result_dict = {}
    filename_to_load = 'placeholder.json'
    for file in os.listdir('tests/data/'):
        if file.startswith('__pytest_to_load_myob_converted_customers_') and file.endswith('.json'):
            filename_to_load = os.path.join('tests/data/', file)
            # break after finding the first match
            break
    with open(filename_to_load, 'r', encoding='utf-8') as f:
        result_dict = json.load(f)
    assert(
        isinstance(result_dict, dict)
    )
    # now import the invoices
    imported_invoices = entry.myob_api_modules.convert_splose_invoice_to_myob_invoice(
        access_token=os.environ.get('myob_pytest_access_token',''),
        business_id=os.environ.get('myob_pytest_business_id',''),
        splose_invoice_dict_list=pending_invoices,
        customer_uid_map=result_dict
    )
    assert(
        isinstance(imported_invoices, dict)
    )
    # save the result to a pretty formatted json file for manual inspection
    now = datetime.datetime.now()
    filename = f"tests/data/__expected_myob_imported_invoices_{now.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(imported_invoices, f, ensure_ascii=False, indent=4)

def test_get_customer_payments_after_date_and_convert_to_invoice_key(entry):
    after_date = datetime.datetime.now() - datetime.timedelta(days=20)
    resp = entry.myob_api_modules.get_customer_payments_after_date_and_convert_to_invoice_key(
        access_token=os.environ.get('myob_pytest_access_token',''),
        business_id=os.environ.get('myob_pytest_business_id',''),
        after_date=after_date
    )
    assert(isinstance(resp, dict))
    assert(len(resp) >= 0)
    # save the result to a pretty formatted json file for loading to another test later
    now = datetime.datetime.now()
    filename = f"tests/data/__pytest_to_load_myob_payments_after_{after_date.strftime('%Y%m%d')}_{now.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(resp, f, ensure_ascii=False, indent=4)