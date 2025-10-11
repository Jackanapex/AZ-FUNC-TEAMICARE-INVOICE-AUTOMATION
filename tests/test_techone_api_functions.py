import azure.functions as func
import logging
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn
from test_utils import _save_json_result_to_local_csv_file

def test_func_techone_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_main.build().get_user_function()
    req = MockTimer()
    queuestr = MockOut()
    blobstr = MockOut()
    blobinstr = '1'
    _ = func_call(req,
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

def test_func_techone_export_all_employees_leave_records(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_all_employees_leave_records.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"COMPANY_CODE":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_most_recent_employee_position_status(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_most_recent_employee_position_status.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMPLOYEEID":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))
    # _save_json_result_to_local_csv_file(blobstr.val, "test_func_techone_export_most_recent_employee_position_status")

def test_func_techone_export_plena_employee_most_recent_position_status(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_plena_employee_most_recent_position_status.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMPLOYEEID":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))
    # _save_json_result_to_local_csv_file(blobstr.val, "test_func_techone_export_plena_employee_most_recent_position_status")

def test_func_techone_export_pl_period_balances(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_pl_period_balances.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"LEDGERNAME":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_employee_position_history_enquiry(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_employee_position_history_enquiry.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMPLOYEEID":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))
    # _save_json_result_to_local_csv_file(blobstr.val, "test_func_techone_export_employee_position_history_enquiry")

def test_func_techone_export_plena_employee_position_history_enquiry(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_plena_employee_position_history_enquiry.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMPLOYEEID":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))
    # _save_json_result_to_local_csv_file(blobstr.val, "test_func_techone_export_plena_employee_position_history_enquiry")

def test_func_techone_export_employee_pay_trans(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_employee_pay_trans.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMP_ID":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))
    # now use json.loads to load blobstr.val and save it as a table to output.csv
    # import json
    # import csv
    # data = json.loads(blobstr.val)
    # with open(f"output-page-{req.body}.csv", 'w', newline='') as f:
    #     csvwriter = csv.writer(f)
    #     count = 0
    #     for emp in data:
    #         if count == 0:
    #             header = emp.keys()
    #             csvwriter.writerow(header)
    #             count += 1
    #         csvwriter.writerow(emp.values())

def test_func_techone_export_plena_inv_header(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_plena_inv_header.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"LEDGER":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_plena_inv_lines(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_plena_inv_lines.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"DOCUMENT_FILE_NAME":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_employee_leave_balances(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_employee_leave_balances.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"HREMPLOYEEACCRUALBALANCESREPORTING_lveentEmployeeId":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_pay_transactions_ba(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_pay_transactions_ba.build().get_user_function()
    req = MockIn('030')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"EMPLOYEEID": '
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

def test_func_techone_export_cp_period_balances(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_cp_period_balances.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"PERIODBALANCES_F1La_LedgerName":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))    

def test_func_techone_export_pl_period_balances_x(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_export_pl_period_balances_x.build().get_user_function()
    req = MockIn('001')
    blobstr = MockOut()
    queuestr = MockOut()
    outblobstr = MockOut()
    _ = func_call(blobstr, queuestr, req, outblobstr)                                                                              
    # Check the output.
    expected_start = '[{"PERIODBALANCES_F1La_LedgerName":'
    assert(queuestr.val.startswith('200 - '))
    assert(blobstr.val.startswith(expected_start))

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