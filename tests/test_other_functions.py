import azure.functions as func
import logging

from test_utils import MockTimer
from test_utils import MockOut
from test_utils import MockIn

def test_func_zenitas_public_holiday_calendar_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_zenitas_public_holiday_calendar_main.build().get_user_function()
    req = MockTimer()
    blobstr = MockOut()
    _ = func_call(req, blobstr)
    delimiter = '\n'
    logging.info(f"Output:\n{delimiter.join(blobstr.val.splitlines()[:3])}\n...")
    # Check the output.
    assert(blobstr.val.startswith('state,date,holiday_name\nNATIONAL,'))

def test_func_zenitas_base_calendar_main(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_zenitas_base_calendar_main.build().get_user_function()
    req = MockTimer()
    blobstr = MockOut()
    _ = func_call(req, blobstr)
    delimiter = '\n'
    logging.info(f"Output:\n{delimiter.join(blobstr.val.splitlines()[:3])}\n...")
    # Check the output.
    assert(blobstr.val.startswith('calendar_date,calendar_date_identifier,year_day,quarter_day,month_day,claro_fortnight_day,plena_fortnight_day,iso8601_weekday,weekday_name,weekday_name_short,calendar_year,year_identifier,year_starting,year_ending,year_is_leap,year_num_of_days,fiscal_year,fiscal_year_identifier,fiscal_year_starting,fiscal_year_ending,fiscal_year_num_of_days,calendar_quarter,quarter_identifier,quarter_starting,quarter_ending,quarter_num_of_days,calendar_month,month_identifier,month_name,month_name_short,month_starting,month_ending,month_num_of_days,claro_fortnight_identifier,claro_fortnight_starting,claro_fortnight_ending,plena_fortnight_identifier,plena_fortnight_starting,plena_fortnight_ending,iso8601_week_year,iso8601_week,iso8601_week_identifier,week_starting,week_ending\n'))

def test_func_livehire_run_results(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_livehire_run_results.build().get_user_function()
    req = MockIn('This is a testing queue message.')
    outblobstr = MockOut()
    _ = func_call(req, outblobstr)                                                                              
    # Check the output.
    assert(outblobstr.val.encode('utf-8') == req.get_body())

def test_func_salesforce_dimple_run_results(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_dimple_run_results.build().get_user_function()
    req = MockIn('This is a testing queue message.')
    outblobstr = MockOut()
    _ = func_call(req, outblobstr)                                                                              
    # Check the output.
    assert(outblobstr.val.encode('utf-8') == req.get_body())

def test_func_salesforce_plena_run_results(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_salesforce_plena_run_results.build().get_user_function()
    req = MockIn('This is a testing queue message.')
    outblobstr = MockOut()
    _ = func_call(req, outblobstr)                                                                              
    # Check the output.
    assert(outblobstr.val.encode('utf-8') == req.get_body())

def test_func_techone_run_results(entry):
    """ This example shows how test case works. """
    # Call the function.
    func_call = entry.func_techone_run_results.build().get_user_function()
    req = MockIn('This is a testing queue message.')
    outblobstr = MockOut()
    _ = func_call(req, outblobstr)                                                                              
    # Check the output.
    assert(outblobstr.val.encode('utf-8') == req.get_body())