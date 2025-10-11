import azure.functions as func
import logging
import os
from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn
from datetime import datetime as dt

def test_authenticate_web_sharepoint_session(entry):
    """ This example shows how test case works. """
    # Call the function.
    resp = entry.sharepoint_api_modules._authenticate_web_sharepoint_session(os.environ['sharepoint_site_url'],
                                                                             os.environ['sharepoint_username'],
                                                                             os.environ['sharepoint_password'])
    # Check the output.
    assert(resp.web.get().execute_query().url.startswith(os.environ['sharepoint_site_url']))
    

def test_func_sharepoint_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_sharepoint_main.build().get_user_function()
    req = MockTimer()
    queuestr_0 = MockOut()
    queuestr_1 = MockOut()
    blobstr_0 = MockOut()
    blobstr_1 = MockOut()
    blobstr = '2025-01-15 00:00:00'
    _ = func_call(req, 
                  blobstr, blobstr,
                  queuestr_0, queuestr_1,
                  blobstr_0, blobstr_1)
    # Check the output.
    assert(isinstance(queuestr_0.val, list))
    assert(isinstance(queuestr_1.val, list))
    assert(blobstr_0.val.startswith(dt.strftime(dt.now(), "%Y-%m-%d ")))
    assert(blobstr_1.val.startswith(dt.strftime(dt.now(), "%Y-%m-%d ")))

def test_func_sharepoint_export_claro_wip_master_roster(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_sharepoint_export_claro_wip_master_roster.build().get_user_function()
    queue_trigger = MockIn('WIP_MASTER_ROSTER_20250214_110500.csv')
    queuestr = MockOut()
    blobstr_0 = MockOut()
    blobstr_1 = MockOut()
    _ = func_call(blobstr_0, queuestr, queue_trigger, blobstr_1)
    # Check the output.
    assert(blobstr_0.val.startswith('client_hub,client_id,client_name,employee_id,employee,week_of_fortnight,day_of_week,start_time,end_time,duration,service_code_name,casual_to_ppt_conversion,recruitment_id'))
    assert(queuestr.val.startswith(f"File {os.environ['sharepoint_folder_claro_wip_master_roster']}"))
    assert(blobstr_1.val is None)

def test_func_sharepoint_export_plena_kpi_target(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_sharepoint_export_plena_kpi_target.build().get_user_function()
    queue_trigger = MockIn('plena_targets_25_upload_2025_01_31.csv')
    queuestr = MockOut()
    blobstr_0 = MockOut()
    blobstr_1 = MockOut()
    _ = func_call(blobstr_0, queuestr, queue_trigger, blobstr_1)
    # Check the output.
    assert(blobstr_0.val.startswith('fortnight_end_date,modality,target_kpi,expense_code,daily_billable_hours_target'))
    assert(queuestr.val.startswith(f"File {os.environ['sharepoint_folder_plena_kpi_target']}"))
    assert(blobstr_1.val is None)

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