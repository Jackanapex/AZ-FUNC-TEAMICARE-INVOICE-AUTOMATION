import azure.functions as func
import logging
import os
import json
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

from this_app_module import livehire_api_modules
from this_app_module import livehire_api_authentication
from this_app_module import zenitas_public_holiday_calendar_modules
from this_app_module import techone_api_modules
from this_app_module import salesforce_api_modules
from this_app_module import sharepoint_api_modules
from this_app_module import alayacare_api_modules
from this_app_module import splose_api_modules

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
def func_splose_all_awaiting_payment_invoices(myTimer: func.TimerRequest):
    if myTimer.past_due:
        logging.info('The timer is past due!')
    secret = os.environ["splose_api_secret"]
    result_invoice_list = splose_api_modules.list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_invoices"], 
        secret, [], params = {'status': 'Awaiting Payment'})
    logging.info(f"Number of invoices with Awaiting Payment status: {len(result_invoice_list)}")
    result_contact_list = splose_api_modules.list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_contacts"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of contacts retrieved: {len(result_contact_list)}")
    result_patient_list = splose_api_modules.list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_patients"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of patients retrieved: {len(result_patient_list)}")
    result_practitioner_list = splose_api_modules.list_objects_from_splose(
        os.environ["splose_api_url"], 
        os.environ["splose_api_url_list_practitioners"], 
        secret, [], params = {'include_archived': 'true'})
    logging.info(f"Number of practitioners retrieved: {len(result_practitioner_list)}")
    # convert result_invoice_list to a flat dataframe
    df_invoices = pd.json_normalize(result_invoice_list)
    df_contacts = pd.json_normalize(result_contact_list)
    df_patients = pd.json_normalize(result_patient_list)
    df_practitioners = pd.json_normalize(result_practitioner_list)
    if len(df_invoices) > 0:
        df_merged = df_invoices.merge(df_contacts[['id', 'type', 'name', 'companyName', 'email', 'phoneNumbers', 'country']], how='left', left_on='contactId', right_on='id', suffixes=('', '_contact'))
        df_merged = df_merged.merge(df_patients[['id', 'title', 'firstname', 'lastname', 'sex', 'email', 'phoneNumbers', 'timezone', 'country']], how='left', left_on='patientId', right_on='id', suffixes=('', '_patient'))
        df_merged = df_merged.merge(df_practitioners[['id', 'title', 'firstname', 'lastname', 'profession', 'email', 'roleName', 'timezone']], how='left', left_on='practitionerId', right_on='id', suffixes=('', '_practitioner'))
        df_merged = df_merged.drop(columns=['id_contact', 'id_patient', 'id_practitioner'])
        # convert the issueDate and due_date to datetime format
        # df_merged['issueDate'] = pd.to_datetime(df_merged['issueDate']).dt.date
        # df_merged['dueDate'] = pd.to_datetime(df_merged['dueDate']).dt.date
        # convert the total and balance to numeric format
        # df_merged['subtotal'] = pd.to_numeric(df_merged['subtotal'])
        # df_merged['total'] = pd.to_numeric(df_merged['total'])
        # df_merged['tax'] = pd.to_numeric(df_merged['tax'])
        # sort the dataframe by due_date ascending
        df_merged = df_merged.sort_values(by=['dueDate'])
        # convert the dataframe to a list of dictionaries
        result_list = df_merged.to_dict(orient='records')
    else:
        logging.info("No invoices with Awaiting Payment status found.")
    return result_list





############################################################################################################
# The following functions are the main functions that are triggered by the timer trigger
############################################################################################################

@app.function_name(name="func_zenitas_base_calendar_main")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_output(arg_name="outputblob",
                path="zenitas/base_calendar/base_calendar_{DateTime}.csv",
                connection="AzureWebJobsStorage")
def func_zenitas_base_calendar_main(myTimer: func.TimerRequest, outputblob: func.Out[str]) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    result = zenitas_public_holiday_calendar_modules._get_base_calendar()
    outputblob.set(result)

@app.function_name(name="func_zenitas_public_holiday_calendar_main")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_output(arg_name="outputblob",
                path="zenitas/public_holiday_calendar/public_holiday_calendar_{DateTime}.csv",
                connection="AzureWebJobsStorage")
def func_zenitas_public_holiday_calendar_main(myTimer: func.TimerRequest, outputblob: func.Out[str]) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    result = zenitas_public_holiday_calendar_modules._get_holiday_calendar()
    outputblob.set(result)

@app.function_name(name="func_sharepoint_main")
@app.timer_trigger(schedule="0 10 * * * 1-5", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_input(arg_name="inputblobdateClaroWipMasterRoster",
                path="zenitas-sharepoint-datetime-record/claro_wip_master_roster.txt",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobdatePlenaKpiTarget",
                path="zenitas-sharepoint-datetime-record/plena_kpi_target.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgSharepointTriggerClaroWipMasterRoster", 
                  queue_name="sharepoint-trigger-claro-wip-master-roster", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgSharepointTriggerPlenaKpiTarget", 
                  queue_name="sharepoint-trigger-plena-kpi-target", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobdateClaroWipMasterRoster",
                path="zenitas-sharepoint-datetime-record/claro_wip_master_roster.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobdatePlenaKpiTarget",
                path="zenitas-sharepoint-datetime-record/plena_kpi_target.txt",
                connection="AzureWebJobsStorage")
def func_sharepoint_main(
    myTimer: func.TimerRequest,
    inputblobdateClaroWipMasterRoster: str,
    inputblobdatePlenaKpiTarget: str,
    msgSharepointTriggerClaroWipMasterRoster: func.Out[func.QueueMessage],
    msgSharepointTriggerPlenaKpiTarget: func.Out[func.QueueMessage],
    outputblobdateClaroWipMasterRoster: func.Out[str],
    outputblobdatePlenaKpiTarget: func.Out[str]
    ) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    def _get_file_list(ctx, inputblob, outputTrigger, folder, filetype, name, outputblob, default_start_time = '2025-01-01 00:00:00'):
        # get all files' relative urls meeting ingest criteria
        start_time = inputblob if inputblob is not None else default_start_time
        outputblob.set(dt.now().strftime("%Y-%m-%d %H:%M:%S"))
        file_list = sharepoint_api_modules._get_web_all_items(ctx, folder, start_time, filetype)
        if len(file_list) > 0:
            trigger_output = [file['file'][len(folder):].replace('/','|') for file in file_list]
            logging.info(f"Triggering {name} files: {trigger_output}")
            outputTrigger.set(trigger_output)
        else:
            logging.info(f"No new files found for {name}")
            outputTrigger.set([])

    ctx = sharepoint_api_modules._authenticate_web_sharepoint_session(
        os.environ['sharepoint_site_url'],
        os.environ['sharepoint_username'],
        os.environ['sharepoint_password']
    )
    if ctx:
        # get all files' relative urls meeting ingest criteria for Claro WIP Master Roster
        _get_file_list(ctx, inputblobdateClaroWipMasterRoster, msgSharepointTriggerClaroWipMasterRoster,
                      os.environ['sharepoint_folder_claro_wip_master_roster'],
                      os.environ['sharepoint_file_type_claro_wip_master_roster'],
                      'Claro WIP Master Roster', outputblobdateClaroWipMasterRoster)

        # get all files' relative urls meeting ingest criteria for Plena KPI Target
        _get_file_list(ctx, inputblobdatePlenaKpiTarget, msgSharepointTriggerPlenaKpiTarget,
                      os.environ['sharepoint_folder_plena_kpi_target'],
                      os.environ['sharepoint_file_type_plena_kpi_target'],
                      'Plena KPI Target', outputblobdatePlenaKpiTarget)
    else:
        logging.info("Failed to authenticate")

@app.function_name(name="func_techone_main")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.queue_output(arg_name="msgTechoneTriggerAllEmployeesLeaveRecords", 
                  queue_name="techone-trigger-all-employees-leave-records", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageAllEmployeesLeaveRecords",
                path="techone-trigger-page-record/all_employees_leave_records.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageAllEmployeesLeaveRecords",
                path="techone-trigger-page-record/all_employees_leave_records.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPlenaEmployeeMostRecentPositionStatus", 
                  queue_name="techone-trigger-plena-employee-most-recent-position-status", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaEmployeeMostRecentPositionStatus",
                path="techone-trigger-page-record/plena_employee_most_recent_position_status.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaEmployeeMostRecentPositionStatus",
                path="techone-trigger-page-record/plena_employee_most_recent_position_status.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerMostRecentEmployeePositionStatus", 
                  queue_name="techone-trigger-most-recent-employee-position-status", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageMostRecentEmployeePositionStatus",
                path="techone-trigger-page-record/most_recent_employee_position_status.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageMostRecentEmployeePositionStatus",
                path="techone-trigger-page-record/most_recent_employee_position_status.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPLPeriodBalances", 
                  queue_name="techone-trigger-pl-period-balances", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePLPeriodBalances",
                path="techone-trigger-page-record/pl_period_balances.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePLPeriodBalances",
                path="techone-trigger-page-record/pl_period_balances.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPlenaEmployeePositionHistoryEnquiry", 
                  queue_name="techone-trigger-plena-employee-position-history-enquiry", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/plena_employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/plena_employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerEmployeePositionHistoryEnquiry", 
                  queue_name="techone-trigger-employee-position-history-enquiry", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerEmployeePayTrans", 
                  queue_name="techone-trigger-employee-pay-trans", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageEmployeePayTrans",
                path="techone-trigger-page-record/employee_pay_trans.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeePayTrans",
                path="techone-trigger-page-record/employee_pay_trans.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPlenaInvHeader", 
                  queue_name="techone-trigger-plena-inv-header", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaInvHeader",
                path="techone-trigger-page-record/plena_inv_header.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaInvHeader",
                path="techone-trigger-page-record/plena_inv_header.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPlenaInvLines", 
                  queue_name="techone-trigger-plena-inv-lines", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaInvLines",
                path="techone-trigger-page-record/plena_inv_lines.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaInvLines",
                path="techone-trigger-page-record/plena_inv_lines.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerEmployeeLeaveBalances", 
                  queue_name="techone-trigger-employee-leave-balances", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageEmployeeLeaveBalances",
                path="techone-trigger-page-record/employee_leave_balances.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeeLeaveBalances",
                path="techone-trigger-page-record/employee_leave_balances.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPayTransactionsBA", 
                  queue_name="techone-trigger-pay-transactions-ba", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePayTransactionsBA",
                path="techone-trigger-page-record/pay_transactions_ba.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePayTransactionsBA",
                path="techone-trigger-page-record/pay_transactions_ba.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerCPPeriodBalances", 
                  queue_name="techone-trigger-cp-period-balances", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageCPPeriodBalances",
                path="techone-trigger-page-record/cp_period_balances.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageCPPeriodBalances",
                path="techone-trigger-page-record/cp_period_balances.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTechoneTriggerPLPeriodBalancesX", 
                  queue_name="techone-trigger-pl-period-balances-x", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePLPeriodBalancesX",
                path="techone-trigger-page-record/pl_period_balances_x.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePLPeriodBalancesX",
                path="techone-trigger-page-record/pl_period_balances_x.txt",
                connection="AzureWebJobsStorage")
def func_techone_main(
        myTimer: func.TimerRequest, 
        msgTechoneTriggerAllEmployeesLeaveRecords: func.Out[func.QueueMessage],
        inputblobpageAllEmployeesLeaveRecords: str,
        outputblobpageAllEmployeesLeaveRecords: func.Out[str],
        msgTechoneTriggerPlenaEmployeeMostRecentPositionStatus: func.Out[func.QueueMessage],
        inputblobpagePlenaEmployeeMostRecentPositionStatus: str,
        outputblobpagePlenaEmployeeMostRecentPositionStatus: func.Out[str],
        msgTechoneTriggerMostRecentEmployeePositionStatus: func.Out[func.QueueMessage],
        inputblobpageMostRecentEmployeePositionStatus: str,
        outputblobpageMostRecentEmployeePositionStatus: func.Out[str],
        msgTechoneTriggerPLPeriodBalances: func.Out[func.QueueMessage],
        inputblobpagePLPeriodBalances: str,
        outputblobpagePLPeriodBalances: func.Out[str],
        msgTechoneTriggerPlenaEmployeePositionHistoryEnquiry: func.Out[func.QueueMessage],
        inputblobpagePlenaEmployeePositionHistoryEnquiry: str,
        outputblobpagePlenaEmployeePositionHistoryEnquiry: func.Out[str],
        msgTechoneTriggerEmployeePositionHistoryEnquiry: func.Out[func.QueueMessage],
        inputblobpageEmployeePositionHistoryEnquiry: str,
        outputblobpageEmployeePositionHistoryEnquiry: func.Out[str],
        msgTechoneTriggerEmployeePayTrans: func.Out[func.QueueMessage],
        inputblobpageEmployeePayTrans: str,
        outputblobpageEmployeePayTrans: func.Out[str],
        msgTechoneTriggerPlenaInvHeader: func.Out[func.QueueMessage],
        inputblobpagePlenaInvHeader: str,
        outputblobpagePlenaInvHeader: func.Out[str],
        msgTechoneTriggerPlenaInvLines: func.Out[func.QueueMessage],
        inputblobpagePlenaInvLines: str,
        outputblobpagePlenaInvLines: func.Out[str],
        msgTechoneTriggerEmployeeLeaveBalances: func.Out[func.QueueMessage],
        inputblobpageEmployeeLeaveBalances: str,
        outputblobpageEmployeeLeaveBalances: func.Out[str],
        msgTechoneTriggerPayTransactionsBA: func.Out[func.QueueMessage],
        inputblobpagePayTransactionsBA: str,
        outputblobpagePayTransactionsBA: func.Out[str],
        msgTechoneTriggerCPPeriodBalances: func.Out[func.QueueMessage],
        inputblobpageCPPeriodBalances: str,
        outputblobpageCPPeriodBalances: func.Out[str],
        msgTechoneTriggerPLPeriodBalancesX: func.Out[func.QueueMessage],
        inputblobpagePLPeriodBalancesX: str,
        outputblobpagePLPeriodBalancesX: func.Out[str]
    ) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    suite_id = os.environ["techone_ws_api_p_suite_id"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    
    def _get_pages_and_send_trigger(auth_token, endpoint_name, blobinput, bloboutput, msgoutobj, suite_id = None, warehouse_name = None, table_name = None, page_buffer = 0, full_load = True, page_size = 50000, custom_params = None) -> None:
        target_endpoint = os.environ[endpoint_name]
        logging.info(f'Target ingestion endpoint:{target_endpoint}')
        if suite_id is None:
            # the new RAAS API endpoints
            query_builder = techone_api_modules.TechoneDataQueryWithCustomParams(auth_token, page_size = page_size, custom_params = custom_params)
        else:
            # the legacy WS API endpoints
            query_builder = techone_api_modules.TechoneDataWSQuery(auth_token, suite_id, warehouse_name, table_name, page_size = page_size)

        last_page = techone_api_modules._get_last_page_number(target_endpoint, query_builder.query_header, query_builder.params)
        start_page = 1 if full_load else max(1, min(int(blobinput if blobinput is not None else '1'), last_page - page_buffer))
        logging.info(f"Sending trigger message for {endpoint_name} pages: {[str(i).zfill(3) for i in range(start_page, last_page+1)]}")
        msgoutobj.set([str(i).zfill(3) for i in range(start_page, last_page+1)])
        logging.info(f"write the last page number to blob storage ...{last_page}")
        bloboutput.set(str(last_page))

    # techone_raas_endpoint_all_employees_leave_records
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_all_employees_leave_records',
        inputblobpageAllEmployeesLeaveRecords,
        outputblobpageAllEmployeesLeaveRecords,
        msgTechoneTriggerAllEmployeesLeaveRecords
    )

    # techone_raas_endpoint_plena_employee_most_recent_position_status
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_plena_employee_most_recent_position_status',
        inputblobpagePlenaEmployeeMostRecentPositionStatus,
        outputblobpagePlenaEmployeeMostRecentPositionStatus,
        msgTechoneTriggerPlenaEmployeeMostRecentPositionStatus
    )

    # techone_raas_endpoint_most_recent_employee_position_status
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_most_recent_employee_position_status',
        inputblobpageMostRecentEmployeePositionStatus,
        outputblobpageMostRecentEmployeePositionStatus,
        msgTechoneTriggerMostRecentEmployeePositionStatus
    )

    # techone_raas_endpoint_pl_period_balances
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_pl_period_balances',
        inputblobpagePLPeriodBalances,
        outputblobpagePLPeriodBalances,
        msgTechoneTriggerPLPeriodBalances
    )

    # techone_raas_endpoint_plena_employee_position_history_enquiry
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_plena_employee_position_history_enquiry',
        inputblobpagePlenaEmployeePositionHistoryEnquiry,
        outputblobpagePlenaEmployeePositionHistoryEnquiry,
        msgTechoneTriggerPlenaEmployeePositionHistoryEnquiry
    )

    # techone_raas_endpoint_employee_position_history_enquiry
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_employee_position_history_enquiry',
        inputblobpageEmployeePositionHistoryEnquiry,
        outputblobpageEmployeePositionHistoryEnquiry,
        msgTechoneTriggerEmployeePositionHistoryEnquiry
    )

    # techone_raas_endpoint_employee_leave_balances
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_employee_leave_balances',
        inputblobpageEmployeeLeaveBalances,
        outputblobpageEmployeeLeaveBalances,
        msgTechoneTriggerEmployeeLeaveBalances,
        custom_params = {'p.CompanyCode': 'all'}
    )
    
    # techone_raas_endpoint_pay_transactions_ba
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_pay_transactions_ba',
        inputblobpagePayTransactionsBA,
        outputblobpagePayTransactionsBA,
        msgTechoneTriggerPayTransactionsBA,
        page_size = 20000,
        custom_params = {'p.CompanyCode': 'all'}
    )
    
    # techone_raas_endpoint_cp_period_balances
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_cp_period_balances',
        inputblobpageCPPeriodBalances,
        outputblobpageCPPeriodBalances,
        msgTechoneTriggerCPPeriodBalances,
        page_size = 20000,
        custom_params = {'p.LedgerName': '25CPACT'}
    )
    
    # techone_raas_endpoint_pl_period_balances_x
    _get_pages_and_send_trigger(
        auth_token, 'techone_raas_endpoint_pl_period_balances_x',
        inputblobpagePLPeriodBalancesX,
        outputblobpagePLPeriodBalancesX,
        msgTechoneTriggerPLPeriodBalancesX,
        page_size = 20000,
        custom_params = {'p.LedgerName': '25PLACT'}
    )

    # techone_ws_endpoint_employee_pay_trans
    _get_pages_and_send_trigger(
        auth_token, 'techone_ws_endpoint_employee_pay_trans',
        inputblobpageEmployeePayTrans,
        outputblobpageEmployeePayTrans,
        msgTechoneTriggerEmployeePayTrans,
        suite_id,
        os.environ["techone_ws_endpoint_p_warehouse_name_employee_pay_trans"],
        os.environ["techone_ws_endpoint_p_table_name_employee_pay_trans"],
        page_size = 25000
    )

    # techone_ws_endpoint_plena_inv_header
    _get_pages_and_send_trigger(
        auth_token, 'techone_ws_endpoint_plena_inv_header',
        inputblobpagePlenaInvHeader,
        outputblobpagePlenaInvHeader,
        msgTechoneTriggerPlenaInvHeader,
        suite_id,
        os.environ["techone_ws_endpoint_p_warehouse_name_plena_inv_header"],
        os.environ["techone_ws_endpoint_p_table_name_plena_inv_header"]
    )

    # techone_ws_endpoint_plena_inv_lines
    _get_pages_and_send_trigger(
        auth_token, 'techone_ws_endpoint_plena_inv_lines',
        inputblobpagePlenaInvLines,
        outputblobpagePlenaInvLines,
        msgTechoneTriggerPlenaInvLines,
        suite_id,
        os.environ["techone_ws_endpoint_p_warehouse_name_plena_inv_lines"],
        os.environ["techone_ws_endpoint_p_table_name_plena_inv_lines"],
        page_size = 40000
    )

@app.function_name(name="func_livehire_main")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsActivities", 
                  queue_name="livehire-trigger-analytics-activities", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobVacancies", 
                  queue_name="livehire-trigger-analytics-job-vacancies", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobVacanciesAdditionalFields", 
                  queue_name="livehire-trigger-analytics-job-vacancies-additional-fields", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsHiringManagers", 
                  queue_name="livehire-trigger-analytics-hiring-managers", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobRecruiters", 
                  queue_name="livehire-trigger-analytics-job-recruiters", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobCandidates", 
                  queue_name="livehire-trigger-analytics-job-candidates", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobCandidateStatus", 
                  queue_name="livehire-trigger-analytics-job-candidate-status", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobOffers", 
                  queue_name="livehire-trigger-analytics-job-offers", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsJobOfferAdditionalFields", 
                  queue_name="livehire-trigger-analytics-job-offer-additional-fields", 
                  connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgLivehireTriggerAnalyticsProfiles", 
                  queue_name="livehire-trigger-analytics-profiles", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
def func_livehire_main(myTimer: func.TimerRequest, 
                       msgLivehireTriggerAnalyticsActivities: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobVacancies: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobVacanciesAdditionalFields: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsHiringManagers: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobRecruiters: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobCandidates: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobCandidateStatus: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobOffers: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsJobOfferAdditionalFields: func.Out[func.QueueMessage], 
                       msgLivehireTriggerAnalyticsProfiles: func.Out[func.QueueMessage], 
                       outputblob: func.Out[str]) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    # get authentication token and save in blob storage for reuse
    bearer_token_obj = livehire_api_authentication._get_bearer_token()
    outputblob.set(bearer_token_obj['body']['access_token'])
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    # set the delta load starting date to be one year before the current date
    _delta_load_starting_date = dt.strftime(
        dt.today() - timedelta(days=600),
        '%Y-%m-%d'
    )
    
    def _get_pages_and_send_trigger(bearer_token, endpoint_name, sample_column_names, filters, msgoutobj) -> None:
        query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token)
        target_endpoint = os.environ[endpoint_name]
        logging.info(f'Target ingestion endpoint:{target_endpoint}')
        if len(sample_column_names) > 0:
            query_builder.set_fields(sample_column_names)
        for f in filters:
            query_builder.add_filter(livehire_api_modules._compose_filter_dict(f[0], f[1], f[2]))
        last_page = livehire_api_modules._get_last_page_number(target_endpoint, query_builder.query_header, query_builder.query_body)
        logging.info(f"Sending trigger message for {endpoint_name} pages: {[str(i).zfill(3) for i in range(1, last_page+1)]}")
        msgoutobj.set([str(i).zfill(3) for i in range(1, last_page+1)])

    # livehire_endpoint_analytics_activities
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_activities',
        ['ActivityId'], [['ActivityDate', '>', _delta_load_starting_date]], msgLivehireTriggerAnalyticsActivities)
    # livehire_endpoint_analytics_job_vacancies
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_vacancies',
        ['JobVacancyUuid'], [['Job Opened Date', '>', _delta_load_starting_date]], msgLivehireTriggerAnalyticsJobVacancies)
    # livehire_endpoint_analytics_job_vacancies_additional_fields
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_vacancies_additional_fields',
        ['JobVacancyID'], [], msgLivehireTriggerAnalyticsJobVacanciesAdditionalFields)
    # livehire_endpoint_analytics_hiring_managers
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_hiring_managers',
        ['JobHiringManagerId'], [], msgLivehireTriggerAnalyticsHiringManagers)
    # livehire_endpoint_analytics_job_recruiters
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_recruiters',
        ['JobRecruiterId'], [], msgLivehireTriggerAnalyticsJobRecruiters)
    # livehire_endpoint_analytics_job_candidates
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_candidates',
        ['ConnectedProfileId'], [['Application Date', '>', _delta_load_starting_date]], msgLivehireTriggerAnalyticsJobCandidates)
    # livehire_endpoint_analytics_job_candidate_status
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_candidate_status',
        ['ActivityId'], [['ActivityDate', '>', _delta_load_starting_date]], msgLivehireTriggerAnalyticsJobCandidateStatus)
    # livehire_endpoint_analytics_job_offers
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_offers',
        ['JobOfferUuid'], [], msgLivehireTriggerAnalyticsJobOffers)
    # livehire_endpoint_analytics_job_offer_additional_fields
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_job_offer_additional_fields',
        ['JobOfferUuid'], [], msgLivehireTriggerAnalyticsJobOfferAdditionalFields)
    # livehire_endpoint_analytics_profiles
    _get_pages_and_send_trigger(
        bearer_token_obj['body']['access_token'], 'livehire_endpoint_analytics_profiles',
        ['ConnectedProfileId'], [], msgLivehireTriggerAnalyticsProfiles)

@app.function_name(name="func_salesforce_main")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_output(arg_name="outputblobPlenaSession",
                path="salesforce-plena-session/session.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobDimpleSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerPlenaAccount", 
                  queue_name="salesforce-plena-trigger-account", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaAccount",
                path="salesforce-plena-trigger-page-record/account.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaAccount",
                path="salesforce-plena-trigger-page-record/account.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerPlenaClaroAccommodationC", 
                  queue_name="salesforce-plena-trigger-claro-accommodation-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaClaroAccommodationC",
                path="salesforce-plena-trigger-page-record/claro_accommodation__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaClaroAccommodationC",
                path="salesforce-plena-trigger-page-record/claro_accommodation__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerPlenaBedC", 
                  queue_name="salesforce-plena-trigger-bed-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePlenaBedC",
                path="salesforce-plena-trigger-page-record/bed__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaBedC",
                path="salesforce-plena-trigger-page-record/bed__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerOpportunity", 
                  queue_name="salesforce-plena-trigger-opportunity", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageOpportunity",
                path="salesforce-plena-trigger-page-record/opportunity.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageOpportunity",
                path="salesforce-plena-trigger-page-record/opportunity.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerPatientC", 
                  queue_name="salesforce-dimple-trigger-patient-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpagePatientC",
                path="salesforce-dimple-trigger-page-record/patient__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePatientC",
                path="salesforce-dimple-trigger-page-record/patient__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerUser", 
                  queue_name="salesforce-dimple-trigger-user", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageUser",
                path="salesforce-dimple-trigger-page-record/user.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageUser",
                path="salesforce-dimple-trigger-page-record/user.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerSkedResourceC", 
                  queue_name="salesforce-dimple-trigger-sked-resource-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageSkedResourceC",
                path="salesforce-dimple-trigger-page-record/sked__resource__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageSkedResourceC",
                path="salesforce-dimple-trigger-page-record/sked__resource__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerSkedAvailabilityC", 
                  queue_name="salesforce-dimple-trigger-sked-availability-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageSkedAvailabilityC",
                path="salesforce-dimple-trigger-page-record/sked__availability__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageSkedAvailabilityC",
                path="salesforce-dimple-trigger-page-record/sked__availability__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerContact", 
                  queue_name="salesforce-dimple-trigger-contact", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageContact",
                path="salesforce-dimple-trigger-page-record/contact.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageContact",
                path="salesforce-dimple-trigger-page-record/contact.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerAccount", 
                  queue_name="salesforce-dimple-trigger-account", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageAccount",
                path="salesforce-dimple-trigger-page-record/account.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageAccount",
                path="salesforce-dimple-trigger-page-record/account.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerSkedJobC", 
                  queue_name="salesforce-dimple-trigger-sked-job-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageSkedJobC",
                path="salesforce-dimple-trigger-page-record/sked__job__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageSkedJobC",
                path="salesforce-dimple-trigger-page-record/sked__job__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerSessionC", 
                  queue_name="salesforce-dimple-trigger-session-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageSessionC",
                path="salesforce-dimple-trigger-page-record/session__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageSessionC",
                path="salesforce-dimple-trigger-page-record/session__c.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgTriggerSkedRegionC", 
                  queue_name="salesforce-dimple-trigger-sked-region-c", 
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobpageSkedRegionC",
                path="salesforce-dimple-trigger-page-record/sked__region__c.txt",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageSkedRegionC",
                path="salesforce-dimple-trigger-page-record/sked__region__c.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_main(
        myTimer: func.TimerRequest, 
        outputblobPlenaSession: func.Out[str],
        outputblobDimpleSession: func.Out[str],
        msgTriggerPlenaAccount: func.Out[func.QueueMessage],
        inputblobpagePlenaAccount: str,
        outputblobpagePlenaAccount: func.Out[str],
        msgTriggerPlenaClaroAccommodationC: func.Out[func.QueueMessage],
        inputblobpagePlenaClaroAccommodationC: str,
        outputblobpagePlenaClaroAccommodationC: func.Out[str],
        msgTriggerPlenaBedC: func.Out[func.QueueMessage],
        inputblobpagePlenaBedC: str,
        outputblobpagePlenaBedC: func.Out[str],
        msgTriggerOpportunity: func.Out[func.QueueMessage],
        inputblobpageOpportunity: str,
        outputblobpageOpportunity: func.Out[str],
        msgTriggerPatientC: func.Out[func.QueueMessage],
        inputblobpagePatientC: str,
        outputblobpagePatientC: func.Out[str],
        msgTriggerUser: func.Out[func.QueueMessage],
        inputblobpageUser: str,
        outputblobpageUser: func.Out[str],        
        msgTriggerSkedResourceC: func.Out[func.QueueMessage],
        inputblobpageSkedResourceC: str,
        outputblobpageSkedResourceC: func.Out[str],
        msgTriggerSkedAvailabilityC: func.Out[func.QueueMessage],
        inputblobpageSkedAvailabilityC: str,
        outputblobpageSkedAvailabilityC: func.Out[str],
        msgTriggerContact: func.Out[func.QueueMessage],
        inputblobpageContact: str,
        outputblobpageContact: func.Out[str],
        msgTriggerAccount: func.Out[func.QueueMessage],
        inputblobpageAccount: str,
        outputblobpageAccount: func.Out[str],
        msgTriggerSkedJobC: func.Out[func.QueueMessage],
        inputblobpageSkedJobC: str,
        outputblobpageSkedJobC: func.Out[str],
        msgTriggerSessionC: func.Out[func.QueueMessage],
        inputblobpageSessionC: str,
        outputblobpageSessionC: func.Out[str],
        msgTriggerSkedRegionC: func.Out[func.QueueMessage],
        inputblobpageSkedRegionC: str,
        outputblobpageSkedRegionC: func.Out[str]
    ) -> None:
    EARLIEST_MODIFIED_DATE = dt.strptime('2018-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')

    if myTimer.past_due:
        logging.info('The timer is past due!')
    
    # refresh plena session
    plena_session = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
    plena_session_id, plena_instance = plena_session.renew_session()
    outputblobPlenaSession.set(f"{plena_session_id} {plena_instance}")
    # refresh dimple session
    dimple_session = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
    dimple_session_id, dimple_instance = dimple_session.renew_session()
    outputblobDimpleSession.set(f"{dimple_session_id} {dimple_instance}")

    def _get_pages_and_send_trigger(object_name, blobinput, bloboutput, msgoutobj, history_page_size = 100, delta_page_size = 20, full_load = False) -> None:
        logging.info(f'Target object name:{object_name}')
        blobinput = blobinput if blobinput is not None else dt.strftime(EARLIEST_MODIFIED_DATE, '%Y-%m-%dT%H:%M:%SZ')
        datetime_from = min(EARLIEST_MODIFIED_DATE, dt.strptime(blobinput, '%Y-%m-%dT%H:%M:%SZ')) if full_load else dt.strptime(blobinput, '%Y-%m-%dT%H:%M:%SZ')
        datetime_to = datetime_from + timedelta(days=history_page_size)
        trigger_list = []
        while datetime_to <= dt.today():
            trigger_list.append(f"LastModifiedDate >= {datetime_from.strftime('%Y-%m-%dT%H:%M:%SZ')} and LastModifiedDate < {datetime_to.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            datetime_from = datetime_to
            datetime_to = datetime_from + timedelta(days=history_page_size)
        datetime_to = datetime_from + timedelta(days=delta_page_size)
        while datetime_to <= dt.today() + timedelta(days=1):
            trigger_list.append(f"LastModifiedDate >= {datetime_from.strftime('%Y-%m-%dT%H:%M:%SZ')} and LastModifiedDate < {datetime_to.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            datetime_from = datetime_to
            datetime_to = datetime_from + timedelta(days=delta_page_size)
        if datetime_from <= dt.today():
            trigger_list.append(f"LastModifiedDate = LAST_N_DAYS:{delta_page_size - 1}")
        logging.info(f"Sending trigger message for {object_name} pages: {trigger_list}")
        msgoutobj.set(trigger_list)
        logging.info(f"write the last page number to blob storage ...{datetime_from}")
        bloboutput.set(datetime_from.strftime('%Y-%m-%dT%H:%M:%SZ'))

    _get_pages_and_send_trigger('plena_Account', inputblobpagePlenaAccount, outputblobpagePlenaAccount, msgTriggerPlenaAccount)
    _get_pages_and_send_trigger('plena_Claro_Accommodation__c', inputblobpagePlenaClaroAccommodationC, outputblobpagePlenaClaroAccommodationC, msgTriggerPlenaClaroAccommodationC)
    _get_pages_and_send_trigger('plena_Bed__c', inputblobpagePlenaBedC, outputblobpagePlenaBedC, msgTriggerPlenaBedC)
    _get_pages_and_send_trigger('plena_Opportunity', inputblobpageOpportunity, outputblobpageOpportunity, msgTriggerOpportunity)
    _get_pages_and_send_trigger('dimple_Patient__c', inputblobpagePatientC, outputblobpagePatientC, msgTriggerPatientC)
    _get_pages_and_send_trigger('dimple_User', inputblobpageUser, outputblobpageUser, msgTriggerUser)
    _get_pages_and_send_trigger('dimple_sked__Resource__c', inputblobpageSkedResourceC, outputblobpageSkedResourceC, msgTriggerSkedResourceC)
    _get_pages_and_send_trigger('dimple_sked__Availability__c', inputblobpageSkedAvailabilityC, outputblobpageSkedAvailabilityC, msgTriggerSkedAvailabilityC)
    _get_pages_and_send_trigger('dimple_Contact', inputblobpageContact, outputblobpageContact, msgTriggerContact)
    _get_pages_and_send_trigger('dimple_Account', inputblobpageAccount, outputblobpageAccount, msgTriggerAccount)
    _get_pages_and_send_trigger('dimple_sked__Job__c', inputblobpageSkedJobC, outputblobpageSkedJobC, msgTriggerSkedJobC)
    _get_pages_and_send_trigger('dimple_Session__c', inputblobpageSessionC, outputblobpageSessionC, msgTriggerSessionC)
    _get_pages_and_send_trigger('dimple_sked__Region__c', inputblobpageSkedRegionC, outputblobpageSkedRegionC, msgTriggerSkedRegionC)

############################################################################################################
# The following functions are triggered by the messages sent from the main functions above
############################################################################################################

############################################################################################################
# Livehire Sub Functions
############################################################################################################

@app.function_name(name="func_livehire_api_export_analytics_activities")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-activities",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_activities/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_activities(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])
    _delta_load_starting_date = dt.strftime(
        dt.today() - timedelta(days=600),
        '%Y-%m-%d'
    )

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_activities"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'ActivityId',
            'ActivityTimeStamp',
            'ActivityDate',
            'Activity Category',
            'Activity Type',
            'ConnectedProfileId',
            'JobVacancyUuid',
            'JobCandidateUuid',
            'JobOfferUuid',
            'MovedToJobCandidateStatusId'
        ]
    )
    # set the filter
    query_builder.add_filter(
        livehire_api_modules._compose_filter_dict('ActivityDate', '>', _delta_load_starting_date)
    )

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage and message queue
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_vacancies")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-vacancies",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_vacancies/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_vacancies(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])
    _delta_load_starting_date = dt.strftime(
        dt.today() - timedelta(days=600),
        '%Y-%m-%d'
    )

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_vacancies"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobVacancyUuid',
            'Job Id',
            'Collaborators',
            'Segment',
            'Recruitment Process',
            'Job Title',
            'Url Code',
            'Expression of Interest',
            'Desired Start Date',
            'Target Days to Hire',
            'JobLocationId',
            'Country',
            'State',
            'Postcode',
            'Suburb',
            'Work Type',
            'Contract Duration',
            'Minimum Remuneration',
            'Maximum Remuneration',
            'Remuneration Package',
            'Internal Notes',
            'Category',
            'SubCategory',
            'Cost Centre',
            'Job Status',
            'Positions',
            'Filled Positions',
            'Unfilled Positions',
            'Days Open',
            'Job Opened Date',
            'Job Closed Date',
            'Job Closed Reason',
            'Job Closed Reason Detail',
            'JobHiringManagerId',
            'JobRecruiterId'
        ]
    )
    # set the filter
    query_builder.add_filter(
        livehire_api_modules._compose_filter_dict('Job Opened Date', '>', _delta_load_starting_date)
    )

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_vacancies_additional_fields")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-vacancies-additional-fields",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_vacancies_additional_fields/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_vacancies_additional_fields(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_vacancies_additional_fields"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobVacancyUuid',
            'JobVacancyID',
            'CostCentre',
            'Furtherinfo',
            'Languages',
            'Name',
            'Languagestwo',
            'Comments',
            'Details',
            'AdditionalDetails',
            'ReportingManager',
            'Facility',
            'DaysTimes',
            'Competency',
            'Projectacg',
            'Project',
            'Active',
            'Programtwo',
            'Program',
            'Programtwoacg',
            'Gender',
            'Gendertwo',
            'Brand',
            'Modality',
            'Brandact',
            'Car',
            'Industry',
            'WorkingWeek',
            'NSWRegion',
            'SiteNSWMetro',
            'SiteVicEast',
            'SiteVicNorth',
            'SiteWA',
            'SiteNswnorth',
            'SiteQLD',
            'SiteVicMetro',
            'FillPriorityACG',
            'Modalityacg',
            'RPOacg',
            'SiteSA',
            'ACTRegion',
            'Video Interview Template',
            'VICRegion',
            'PositionType',
            'HiringCompany',
            'RPO',
            'FillPriority',
            'JobState',
            'Site',
            'ExpLevel',
            'Job',
            'Department',
            'Division',
            'Pets',
            'Children',
            'Areas',
            'Checks',
            'ForcedAgency',
            'ForcedAgencyacg',
            'Vid Req',
            'AutoInvite',
            'AgencyRequired',
            'Locum',
            'sleepovers',
            'DriversLicense',
            'Hours',
            'Internal',
            'Limtedreg',
            'Locumacg',
            'Region',
            'Japara',
            'Check Template',
            'Check Req',
            'Hub_Names'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_hiring_managers")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-hiring-managers",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_hiring_managers/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_hiring_managers(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_hiring_managers"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobHiringManagerId',
            'Email',
            'First Name',
            'Last Name',
            'Full Name',
            'User Role'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_recruiters")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-recruiters",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_recruiters/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_recruiters(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_recruiters"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobRecruiterId',
            'Email',
            'First Name',
            'Last Name',
            'Full Name',
            'User Role'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_candidates")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-candidates",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_candidates/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_candidates(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])
    _delta_load_starting_date = dt.strftime(
        dt.today() - timedelta(days=600),
        '%Y-%m-%d'
    )
    
    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_candidates"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'ConnectedProfileId',
            'JobCandidateUuid',
            'JobCandidateCurrentStatusId',
            'Candidate Status',
            'Candidate Base Status',
            'Ordered Candidate Status',
            'Is From Talent Pool',
            'Days To Hire',
            'Application Date',
            'StatusLastChangedAt',
            'NotSuitableStatusAt',
            'Unsuccessful',
            'Unsuccessful Notification Status',
            'Days From Marked Unsuccessful to Unsuccessful Notification',
            'Days From Application to Unsuccessful Notification',
            'Filled by Target',
            'Days From Application To Hire',
            'Candidate Source',
            'Candidate Source Group',
            'Rehire',
            'AlreadyInTC'
        ]
    )
    # set the filter
    query_builder.add_filter(
        livehire_api_modules._compose_filter_dict('Application Date', '>', _delta_load_starting_date)
    )
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_candidate_status")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-candidate-status",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_candidate_status/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_candidate_status(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])
    _delta_load_starting_date = dt.strftime(
        dt.today() - timedelta(days=600),
        '%Y-%m-%d'
    )

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_candidate_status"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'ActivityId',
            'JobCandidateId',
            'ActivityTimeStamp',
            'ActivityDate',
            'Updated Candidate Status',
            'Sequence',
            'Updated Candidate Status (Standard)'
        ]
    )
    # set the filter
    query_builder.add_filter(
        livehire_api_modules._compose_filter_dict('ActivityDate', '>', _delta_load_starting_date)
    )
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_offers")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-offers",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_offers/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_offers(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_offers"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobOfferUuid',
            'Job Offer Status',
            'Recruitment Method',
            'Commencement Date',
            'Remuneration Amount',
            'Remuneration Currency',
            'Remuneration Type',
            'Remuneration Type Group',
            'Remuneration Amount (Clean)',
            'Remuneration Salary (Range)',
            'Remuneration Hourly Rate (Range)',
            'Remuneration Daily Rate (Range)',
            'Company or Agency Name',
            'Work Type'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_job_offer_additional_fields")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-job-offer-additional-fields",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_job_offer_additional_fields/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_job_offer_additional_fields(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_job_offer_additional_fields"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'JobOfferUuid',
            'JobOfferId',
            'startdateconfirmed',
            'employingentity',
            'reportstoname',
            'reportstoposition',
            'hoursofwork',
            'award',
            'awardlevel',
            'workerscreeningcompleted',
            'salaryband',
            'category',
            'otherbenefits',
            'workeligibility',
            'otherbenefitsother',
            'rpo',
            'SourceOfHire',
            'visatype',
            'Limtedreg',
            'OSLimtedreg',
            'Locum',
            'OSLimtedregACG',
            'LocumACG',
            'LimtedregACG',
            'Divisions',
            'Templates'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")
    
@app.function_name(name="func_livehire_api_export_analytics_profiles")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="livehire-trigger-analytics-profiles",
                   connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblob",
                path="livehire-trigger-bearer-token/bearer_token.txt",
                connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="livehire", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="livehire/analytics_profiles/api_ingest_{DateTime}_pp_{QueueTrigger}.csv",
                connection="AzureWebJobsStorage")
def func_livehire_api_export_analytics_profiles(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, inputblob: str) -> func.HttpResponse:
    # get authentication token
    bearer_token_from_msg = inputblob
    if bearer_token_from_msg == 'mock_bearer_token':
        bearer_token_obj = livehire_api_authentication._get_bearer_token()
    else:
        bearer_token_obj = {
            'body': {
                'access_token': bearer_token_from_msg
            }
        }
    logging.info(f"Bearer token is obtained ...{bearer_token_obj['body']['access_token'][:5]}")
    query_builder = livehire_api_modules.LivehireDataQueryBuilder(bearer_token_obj['body']['access_token'])

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["livehire_endpoint_analytics_profiles"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the fields to be queried
    query_builder.set_fields(
        [
            'ConnectedProfileId',
            'Year of Birth',
            'Age (Group)',
            'ATSI',
            'Desired Salary',
            'Desired Salary Range',
            'Years of Experience',
            'Willing to Relocate',
            'Current Job Title',
            'Temporary Profile',
            'Profile Strength',
            'Profile Completion',
            'Preferred Work Types',
            'Full Name',
            'Australian Citizen or Permanent Resident',
            'Connection Status',
            'Rating',
            'Relationship',
            'Pipeline Status',
            'Gender',
            'Availability',
            'Notice Period',
            'Country',
            'State',
            'Suburb',
            'Postcode',
            'Application Count',
            'Application Count (Group)',
            'Application Volume'
        ]
    )
    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = livehire_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.query_body
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(resp.text)
    msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(resp.text.splitlines())} rows")

############################################################################################################
# TechOne Sub Functions
############################################################################################################

@app.function_name(name="func_techone_export_all_employees_leave_records")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-all-employees-leave-records",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/all_employees_leave_records/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageAllEmployeesLeaveRecords",
                path="techone-trigger-page-record/all_employees_leave_records.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_all_employees_leave_records(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageAllEmployeesLeaveRecords: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_all_employees_leave_records"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageAllEmployeesLeaveRecords.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_most_recent_employee_position_status")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-most-recent-employee-position-status",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/most_recent_employee_position_status/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageMostRecentEmployeePositionStatus",
                path="techone-trigger-page-record/most_recent_employee_position_status.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_most_recent_employee_position_status(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageMostRecentEmployeePositionStatus: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_most_recent_employee_position_status"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageMostRecentEmployeePositionStatus.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_plena_employee_most_recent_position_status")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-plena-employee-most-recent-position-status",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/plena_employee_most_recent_position_status/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaEmployeeMostRecentPositionStatus",
                path="techone-trigger-page-record/plena_employee_most_recent_position_status.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_plena_employee_most_recent_position_status(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePlenaEmployeeMostRecentPositionStatus: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_plena_employee_most_recent_position_status"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePlenaEmployeeMostRecentPositionStatus.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_pl_period_balances")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-pl-period-balances",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/pl_period_balances/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePLPeriodBalances",
                path="techone-trigger-page-record/pl_period_balances.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_pl_period_balances(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePLPeriodBalances: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_pl_period_balances"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePLPeriodBalances.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_employee_position_history_enquiry")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-employee-position-history-enquiry",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/employee_position_history_enquiry/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_employee_position_history_enquiry(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageEmployeePositionHistoryEnquiry: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_employee_position_history_enquiry"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageEmployeePositionHistoryEnquiry.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")

@app.function_name(name="func_techone_export_plena_employee_position_history_enquiry")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-plena-employee-position-history-enquiry",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/plena_employee_position_history_enquiry/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaEmployeePositionHistoryEnquiry",
                path="techone-trigger-page-record/plena_employee_position_history_enquiry.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_plena_employee_position_history_enquiry(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePlenaEmployeePositionHistoryEnquiry: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQuery(auth_token)

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_plena_employee_position_history_enquiry"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter

    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePlenaEmployeePositionHistoryEnquiry.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_employee_pay_trans")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-employee-pay-trans",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/employee_pay_trans/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeePayTrans",
                path="techone-trigger-page-record/employee_pay_trans.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_employee_pay_trans(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageEmployeePayTrans: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_ws_api_auth_token"]
    suite_id = os.environ["techone_ws_api_p_suite_id"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    # set the endpoint api warehouse and table name
    warehouse_name = os.environ["techone_ws_endpoint_p_warehouse_name_employee_pay_trans"]
    table_name = os.environ["techone_ws_endpoint_p_table_name_employee_pay_trans"]
    query_builder = techone_api_modules.TechoneDataWSQuery(auth_token, suite_id, warehouse_name, table_name, 25000)
    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_ws_endpoint_employee_pay_trans"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageEmployeePayTrans.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_plena_inv_header")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-plena-inv-header",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/plena_inv_header/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaInvHeader",
                path="techone-trigger-page-record/plena_inv_header.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_plena_inv_header(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePlenaInvHeader: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_ws_api_auth_token"]
    suite_id = os.environ["techone_ws_api_p_suite_id"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    # set the endpoint api warehouse and table name
    warehouse_name = os.environ["techone_ws_endpoint_p_warehouse_name_plena_inv_header"]
    table_name = os.environ["techone_ws_endpoint_p_table_name_plena_inv_header"]
    query_builder = techone_api_modules.TechoneDataWSQuery(auth_token, suite_id, warehouse_name, table_name)
    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_ws_endpoint_plena_inv_header"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePlenaInvHeader.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_plena_inv_lines")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-plena-inv-lines",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/plena_inv_lines/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePlenaInvLines",
                path="techone-trigger-page-record/plena_inv_lines.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_plena_inv_lines(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePlenaInvLines: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_ws_api_auth_token"]
    suite_id = os.environ["techone_ws_api_p_suite_id"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    # set the endpoint api warehouse and table name
    warehouse_name = os.environ["techone_ws_endpoint_p_warehouse_name_plena_inv_lines"]
    table_name = os.environ["techone_ws_endpoint_p_table_name_plena_inv_lines"]
    query_builder = techone_api_modules.TechoneDataWSQuery(auth_token, suite_id, warehouse_name, table_name, 40000)
    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_ws_endpoint_plena_inv_lines"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))
    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        outputblob.set(json.dumps(json.loads(resp.text)['DataSet']))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(json.loads(resp.text)['DataSet'])}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePlenaInvLines.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
    
@app.function_name(name="func_techone_export_employee_leave_balances")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-employee-leave-balances",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/employee_leave_balances/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageEmployeeLeaveBalances",
                path="techone-trigger-page-record/employee_leave_balances.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_employee_leave_balances(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageEmployeeLeaveBalances: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQueryWithCustomParams(auth_token = auth_token, custom_params = {'p.CompanyCode': 'all'})

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_employee_leave_balances"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter
    result_filter_exclude = set()
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        result_json = json.loads(resp.text)['DataSet']
        filtered_result_json = [record for record in result_json if record['HREMPLOYEEACCRUALBALANCESREPORTING_posactvCompanyCode'] not in result_filter_exclude]
        outputblob.set(json.dumps(filtered_result_json))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(filtered_result_json)}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageEmployeeLeaveBalances.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
     
@app.function_name(name="func_techone_export_pay_transactions_ba")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-pay-transactions-ba",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/pay_transactions_ba/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePayTransactionsBA",
                path="techone-trigger-page-record/pay_transactions_ba.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_pay_transactions_ba(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePayTransactionsBA: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQueryWithCustomParams(auth_token = auth_token, page_size = 20000, custom_params = {'p.CompanyCode': 'all'})

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_pay_transactions_ba"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter
    result_filter_exclude = set()
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        result_json = json.loads(resp.text)['DataSet']
        filtered_result_json = [record for record in result_json if record['COMPANYCODE'] not in result_filter_exclude]
        outputblob.set(json.dumps(filtered_result_json))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(filtered_result_json)}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePayTransactionsBA.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
     
@app.function_name(name="func_techone_export_cp_period_balances")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-cp-period-balances",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/cp_period_balances/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpageCPPeriodBalances",
                path="techone-trigger-page-record/cp_period_balances.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_cp_period_balances(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpageCPPeriodBalances: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQueryWithCustomParams(auth_token = auth_token, page_size = 20000, custom_params = {'p.LedgerName': '25CPACT'})

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_cp_period_balances"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter
    result_filter_exclude = set()
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        result_json = json.loads(resp.text)['DataSet']
        filtered_result_json = [record for record in result_json if record['PERIODBALANCES_F1La_LedgerName'] not in result_filter_exclude]
        outputblob.set(json.dumps(filtered_result_json))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(filtered_result_json)}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpageCPPeriodBalances.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
     
@app.function_name(name="func_techone_export_pl_period_balances_x")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="techone-trigger-pl-period-balances-x",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="techone", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="techone/pl_period_balances_x/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpagePLPeriodBalancesX",
                path="techone-trigger-page-record/pl_period_balances_x.txt",
                connection="AzureWebJobsStorage")
def func_techone_export_pl_period_balances_x(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobpagePLPeriodBalancesX: func.Out[str]) -> func.HttpResponse:
    # get authentication token
    auth_token = os.environ["techone_raas_api_auth_token"]
    logging.info(f"Auth token is obtained ...{auth_token[:5]}")
    query_builder = techone_api_modules.TechoneDataQueryWithCustomParams(auth_token = auth_token, page_size = 20000, custom_params = {'p.LedgerName': '25PLACT'})

    # set the endpoint - local dev refer to local.settings.json and in Azure refer to App Service Configuration
    target_endpoint = os.environ["techone_raas_endpoint_pl_period_balances_x"]
    logging.info(f'Target ingestion endpoint:{target_endpoint}')

    # set the filter
    result_filter_exclude = set()
    # set the page
    query_builder.set_page(int(msgin.get_body().decode('utf-8').lstrip('0')))

    # query the data
    resp = techone_api_modules._query_data_from_endpoint(
        target_endpoint,
        query_builder.query_header,
        query_builder.params
    )
    # save to blobstorage
    if resp.status_code == 200:
        result_json = json.loads(resp.text)['DataSet']
        filtered_result_json = [record for record in result_json if record['PERIODBALANCES_F1La_LedgerName'] not in result_filter_exclude]
        outputblob.set(json.dumps(filtered_result_json))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: {len(filtered_result_json)}/{json.loads(resp.text)['TotalRecordCount']} records")
    else:
        outputblobpagePLPeriodBalancesX.set(str(1))
        msgout.set(f"{resp.status_code} - {target_endpoint} - {msgin.get_body().decode('utf-8')}: failed")
     
############################################################################################################
# Salesforce Sub Functions
############################################################################################################

@app.function_name(name="func_salesforce_plena_export_account")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-plena-trigger-account",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-plena", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-plena/account/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-plena-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_plena_export_account(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Account'
    # set the columns
    target_columns = [
        "Id", 
        "OwnerId", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "Level__c",
        "Status__c",
        "Dietetics__c",
        "Physiotherapy__c",
        "Speech_Pathology__c",
        "Podiatry__c",
        "ACFI_Consulting__c",
        "Total_No_of_Beds__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
        query_builder.renew_session()
    query_builder.connect()
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Plena {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Plena {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_plena_export_claro_accommodation__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-plena-trigger-claro-accommodation-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-plena", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-plena/claro_accommodation__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-plena-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_plena_export_claro_accommodation__c(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Claro_Accommodation__c'
    # set the columns
    target_columns = [
        "Id", 
        "OwnerId", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "City__c", 
        "Country__c", 
        "State__c", 
        "Street__c", 
        "Zip_Code__c", 
        "Facility_ID__c", 
        "Accommodation_Operations_Manager__c", 
        "Status__c", 
        "Property_Type__c", 
        "Beds_Filled_Rollup__c", 
        "Planned_Exits_Rollup__c", 
        "Total_Beds_Rollup__c", 
        "Vacant_Beds_Rollup__c", 
        "Accommodation_Services_Lead__c", 
        "Headlease__c", 
        "SDA_Provider__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
        query_builder.renew_session()
    query_builder.connect()
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Plena {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Plena {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_plena_export_bed__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-plena-trigger-bed-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-plena", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-plena/bed__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-plena-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_plena_export_bed__c(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Bed__c'
    # set the columns
    target_columns = [
        "Id", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "Accommodation__c", 
        "Accessability__c", 
        "Bed_Status__c", 
        "Client__c", 
        "Date_Bed_Filled__c", 
        "Date_Bed_Vacated_Onboarded__c", 
        "Planned_Exit_Date__c", 
        "Time_to_Fill__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
        query_builder.renew_session()
    query_builder.connect()
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Plena {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Plena {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_plena_export_opportunity")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-plena-trigger-opportunity",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-plena", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-plena/opportunity/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-plena-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_plena_export_opportunity(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Opportunity'
    # set the columns
    target_columns = [
        "Id", 
        "IsDeleted", 
        "AccountId", 
        "RecordTypeId", 
        "IsPrivate", 
        "Name", 
        "Description", 
        "StageName", 
        "Amount", 
        "Probability", 
        "ExpectedRevenue", 
        "TotalOpportunityQuantity", 
        "CloseDate", 
        "Type", 
        "NextStep", 
        "LeadSource", 
        "IsClosed", 
        "IsWon", 
        "ForecastCategory", 
        "ForecastCategoryName", 
        "CampaignId", 
        "HasOpportunityLineItem", 
        "Pricebook2Id", 
        "OwnerId", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastActivityDate", 
        "FiscalQuarter", 
        "FiscalYear", 
        "Fiscal", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "ContractId", 
        "HasOpenActivity", 
        "HasOverdueTask", 
        "Total_Amount__c", 
        "Existing_Modalities_DEL__c", 
        "No_of_Beds__c", 
        "Areas_of_Operation__c", 
        "Lead_Type__c", 
        "Opportunity_Type__c", 
        "Closed_Lost_Reason__c", 
        "Areas_Count__c", 
        "Prospecting_Modalities__c", 
        "Existing_Areas_of_Operation__c", 
        "Existing_Modalities__c", 
        "Business_Type__c", 
        "Total_No_of_Beds__c", 
        "Modalities_Count__c", 
        "Opportunity_Areas_of_Operation__c", 
        "Opportunity_No_of_Beds__c", 
        "Lead_Amount__c", 
        "No_of_Sites__c", 
        "Client_Segment__c", 
        "Opportunity_No_Sites__c", 
        "Partial_Won__c", 
        "Days_Available__c", 
        "Funding__c", 
        "Further_Information__c", 
        "Preferred_Time_of_Appointment__c", 
        "Funding_Manager__c", 
        "NDIS_End_Date__c", 
        "NDIS_Number__c", 
        "NDIS_Start_Date__c", 
        "Plena_Health_Worker__c", 
        "Related_Contact__c", 
        "Who_made_the_referral__c", 
        "Source_Referral_Account__c", 
        "Accommodation_Listing__c", 
        "Accommodation_State__c", 
        "CEM_Managing__c", 
        "CSM_Assigned__c", 
        "Clinical_Assessment_sent__c", 
        "Community_Hours_Per_Week__c", 
        "Completed_Claro_Referral_form__c", 
        "Confirm_SDA_approval__c", 
        "Confirm_therapist_training_availability__c", 
        "Escalation_to_NDIA_RM_Outside_12_Week__c", 
        "Funding_supp_assmt_SIL_SDA_complete__c", 
        "Intenal_support_doc_training_completed__c", 
        "Management_Type__c", 
        "NDIA_Funding_Appr_confirmed_by_Claro__c", 
        "Prepare_SIL_daily_support_quote__c", 
        "SC_to_arrange_purchase_or_hire_equipment__c", 
        "Seek_approval_of_SIL_daily_support_quote__c", 
        "Services__c", 
        "Stream__c", 
        "Submit_SIL_daily_support_quote_to_NDIA__c", 
        "Support_worker_capacity__c", 
        "Community_Hours_Per_Month__c", 
        "HCP_LEVEL__c", 
        "Name_of_event_conference__c", 
        "Time_until_Package_Assigned__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_plena_username'], password=os.environ['salesforce_plena_password'], security_token=os.environ['salesforce_plena_security_token'])
        query_builder.renew_session()
    query_builder.connect()
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Plena {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Plena {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_patient__c")
@app.queue_trigger(arg_name="msgin",
                   queue_name="salesforce-dimple-trigger-patient-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/patient__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_patient__c(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Patient__c'
    # set the columns
    target_columns = [
        "Id",
        "OwnerId",
        "First_Name__c",
        "Last_Name__c",
        "DOB__c",
        "Facility__c",
        "Status__c",
        "Active__c",
        "Doctor_Surname__c",
        "Doctors_full_Name__c",
        "Facility_Name__c",
        "Duplicate_Finder1__c",
        "Parent_Name__c",
        "Facility_Billingl_City__c",
        "Facility_Billing_Postcode__c",
        "Tableau_Facility_Name__c",
        "Tableau_High_Care_Fee__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_user")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-user",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/user/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_user(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'User'
    # set the columns
    target_columns = [
        "Id", 
        "Username", 
        "LastName", 
        "FirstName", 
        "Name", 
        "CompanyName", 
        "Division", 
        "Department", 
        "Title", 
        "Street", 
        "City", 
        "State", 
        "PostalCode", 
        "Country", 
        "Latitude", 
        "Longitude", 
        "GeocodeAccuracy", 
        "Email", 
        "EmailPreferencesAutoBcc", 
        "EmailPreferencesAutoBccStayInTouch", 
        "EmailPreferencesStayInTouchReminder", 
        "SenderEmail", 
        "SenderName", 
        "Signature", 
        "StayInTouchSubject", 
        "StayInTouchSignature", 
        "StayInTouchNote", 
        "Phone", 
        "Fax", 
        "MobilePhone", 
        "Alias", 
        "CommunityNickname", 
        "BadgeText", 
        "IsActive", 
        "TimeZoneSidKey", 
        "UserRoleId", 
        "LocaleSidKey", 
        "ReceivesInfoEmails", 
        "ReceivesAdminInfoEmails", 
        "EmailEncodingKey", 
        "ProfileId", 
        "UserType", 
        "LanguageLocaleKey", 
        "EmployeeNumber", 
        "DelegatedApproverId", 
        "ManagerId", 
        "LastLoginDate", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "OfflineTrialExpirationDate", 
        "OfflinePdaTrialExpirationDate", 
        "UserPermissionsMarketingUser", 
        "UserPermissionsOfflineUser", 
        "UserPermissionsAvantgoUser", 
        "UserPermissionsCallCenterAutoLogin", 
        "UserPermissionsSFContentUser", 
        "UserPermissionsInteractionUser", 
        "UserPermissionsSupportUser", 
        "UserPermissionsChatterAnswersUser", 
        "ForecastEnabled", 
        "UserPreferencesActivityRemindersPopup", 
        "UserPreferencesEventRemindersCheckboxDefault", 
        "UserPreferencesTaskRemindersCheckboxDefault", 
        "UserPreferencesReminderSoundOff", 
        "UserPreferencesDisableAllFeedsEmail", 
        "UserPreferencesDisableFollowersEmail", 
        "UserPreferencesDisableProfilePostEmail", 
        "UserPreferencesDisableChangeCommentEmail", 
        "UserPreferencesDisableLaterCommentEmail", 
        "UserPreferencesDisProfPostCommentEmail", 
        "UserPreferencesContentNoEmail", 
        "UserPreferencesContentEmailAsAndWhen", 
        "UserPreferencesApexPagesDeveloperMode", 
        "UserPreferencesReceiveNoNotificationsAsApprover", 
        "UserPreferencesReceiveNotificationsAsDelegatedApprover", 
        "UserPreferencesHideCSNGetChatterMobileTask", 
        "UserPreferencesDisableMentionsPostEmail", 
        "UserPreferencesDisMentionsCommentEmail", 
        "UserPreferencesHideCSNDesktopTask", 
        "UserPreferencesHideChatterOnboardingSplash", 
        "UserPreferencesHideSecondChatterOnboardingSplash", 
        "UserPreferencesDisCommentAfterLikeEmail", 
        "UserPreferencesDisableLikeEmail", 
        "UserPreferencesSortFeedByComment", 
        "UserPreferencesDisableMessageEmail", 
        "UserPreferencesDisableBookmarkEmail", 
        "UserPreferencesDisableSharePostEmail", 
        "UserPreferencesEnableAutoSubForFeeds", 
        "UserPreferencesDisableFileShareNotificationsForApi", 
        "UserPreferencesShowTitleToExternalUsers", 
        "UserPreferencesShowManagerToExternalUsers", 
        "UserPreferencesShowEmailToExternalUsers", 
        "UserPreferencesShowWorkPhoneToExternalUsers", 
        "UserPreferencesShowMobilePhoneToExternalUsers", 
        "UserPreferencesShowFaxToExternalUsers", 
        "UserPreferencesShowStreetAddressToExternalUsers", 
        "UserPreferencesShowCityToExternalUsers", 
        "UserPreferencesShowStateToExternalUsers", 
        "UserPreferencesShowPostalCodeToExternalUsers", 
        "UserPreferencesShowCountryToExternalUsers", 
        "UserPreferencesShowProfilePicToGuestUsers", 
        "UserPreferencesShowTitleToGuestUsers", 
        "UserPreferencesShowCityToGuestUsers", 
        "UserPreferencesShowStateToGuestUsers", 
        "UserPreferencesShowPostalCodeToGuestUsers", 
        "UserPreferencesShowCountryToGuestUsers", 
        "UserPreferencesHideS1BrowserUI", 
        "UserPreferencesDisableEndorsementEmail", 
        "UserPreferencesPathAssistantCollapsed", 
        "UserPreferencesCacheDiagnostics", 
        "UserPreferencesShowEmailToGuestUsers", 
        "UserPreferencesShowManagerToGuestUsers", 
        "UserPreferencesShowWorkPhoneToGuestUsers", 
        "UserPreferencesShowMobilePhoneToGuestUsers", 
        "UserPreferencesShowFaxToGuestUsers", 
        "UserPreferencesShowStreetAddressToGuestUsers", 
        "UserPreferencesLightningExperiencePreferred", 
        "UserPreferencesPreviewLightning", 
        "UserPreferencesHideEndUserOnboardingAssistantModal", 
        "UserPreferencesHideLightningMigrationModal", 
        "UserPreferencesHideSfxWelcomeMat", 
        "UserPreferencesHideBiggerPhotoCallout", 
        "UserPreferencesGlobalNavBarWTShown", 
        "UserPreferencesGlobalNavGridMenuWTShown", 
        "UserPreferencesCreateLEXAppsWTShown", 
        "UserPreferencesFavoritesWTShown", 
        "UserPreferencesRecordHomeSectionCollapseWTShown", 
        "UserPreferencesRecordHomeReservedWTShown", 
        "UserPreferencesFavoritesShowTopFavorites", 
        "UserPreferencesExcludeMailAppAttachments", 
        "UserPreferencesSuppressTaskSFXReminders", 
        "UserPreferencesSuppressEventSFXReminders", 
        "UserPreferencesPreviewCustomTheme", 
        "UserPreferencesHasCelebrationBadge", 
        "UserPreferencesUserDebugModePref", 
        "UserPreferencesSRHOverrideActivities", 
        "UserPreferencesNewLightningReportRunPageEnabled", 
        "UserPreferencesReverseOpenActivitiesView", 
        "UserPreferencesNativeEmailClient", 
        "UserPreferencesHideBrowseProductRedirectConfirmation", 
        "UserPreferencesHideOnlineSalesAppWelcomeMat", 
        "ContactId", 
        "AccountId", 
        "CallCenterId", 
        "Extension", 
        "PortalRole", 
        "IsPortalEnabled", 
        "FederationIdentifier", 
        "AboutMe", 
        "FullPhotoUrl", 
        "SmallPhotoUrl", 
        "IsExtIndicatorVisible", 
        "OutOfOfficeMessage", 
        "MediumPhotoUrl", 
        "DigestFrequency", 
        "DefaultGroupNotificationFrequency", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "BannerPhotoUrl", 
        "SmallBannerPhotoUrl", 
        "MediumBannerPhotoUrl", 
        "IsProfilePhotoActive", 
        "Salary_Classification__c", 
        "Signature__c", 
        "ID_photo__c", 
        "Percentage_Available__c", 
        "Level_Banding__c", 
        "Payable_Salary__c", 
        "Daily_Pay_Rate_incl_Super__c", 
        "Count__c", 
        "Apartment_Number__c", 
        "City__c", 
        "Country__c", 
        "State_Province__c", 
        "Street__c", 
        "Zip_Postal_Code__c", 
        "Link_to_User__c", 
        "Productivity_Unavailable_Day_DLRS__c", 
        "Employee_ID__c", 
        "Servicing_Region__c", 
        "Contact_Sync__c", 
        "Create_Contact__c", 
        "Bypass__c", 
        "Manager_Name__c", 
        "Full_Name__c", 
        "Number_of_To_Be_Filled_Days_this_Qtr__c", 
        "Payable_Salary_with_Super__c", 
        "Quarterly_Payable_Salary_w_Super__c", 
        "Provider_Number__c", 
        "Payroll_Comments__c", 
        "Exclude_from_Tier__c", 
        "Tier_Minimum__c", 
        "Tier_Maximum__c", 
        "Working_Days_This_Next_Quarter__c", 
        "Minimum_Treatments_This_Quarter__c", 
        "Working_Days_Last_Quarter__c", 
        "Minimum_Treatments_Last_Quarter__c", 
        "Median_Treatments_Last_Quarter__c", 
        "Maximum_Treatments_Last_Quarter__c", 
        "Maximum_Treatments_This_Quarter__c", 
        "Median_Treatments_This_Quarter__c", 
        "Working_Days__c", 
        "KMS_Travelled__c", 
        "KMS_Travelled_Week_2__c", 
        "KMS_Travelled_Week_3__c", 
        "KMS_Travelled_Week_4__c", 
        "Enable_API__c", 
        "Working_Days_Last_Month__c", 
        "TIMBASURVEYS__SurveyReminder__c", 
        "TIMBASURVEYS__reminderStringSize__c", 
        "Alternate_Delivery_Street__c", 
        "Unduplicated_Count__c", 
        "Home_Address__Latitude__s", 
        "Home_Address__Longitude__s", 
        "Latitude__c", 
        "Longtitude__c", 
        "Alternate_Delivery_City__c", 
        "Alternate_Delivery_State__c", 
        "Alternate_Delivery_Zip_Postal_Code__c", 
        "Special_Delivery_Instructions__c", 
        "Related_Contact_ID__c", 
        "Team__c", 
        "iPro_Live_Compliant__c", 
        "SAFComm_Compliant__c", 
        "Blue_Cross_Compliant__c", 
        "sked__skeduloUserType__c", 
        "Leave_Days_Last_Month__c", 
        "Full_Address__c", 
        "Litmos__Access_Level__c", 
        "Litmos__Completed_Percentage__c", 
        "Litmos__Courses_Assigned__c", 
        "Litmos__Courses_Completed__c", 
        "Litmos__Deactivate_From_Litmos__c", 
        "Litmos__Learning_Paths_Assigned__c", 
        "Litmos__Learning_Paths_Completed__c", 
        "Litmos__LitmosUserId__c", 
        "Litmos__Litmos_Activated__c", 
        "Litmos__Litmos_Login_Access__c", 
        "Litmos__OriginalId__c", 
        "Litmos__Sync_Litmos__c", 
        "Litmos__Team_Id__c", 
        "Litmos__Total_Sum_Percentages__c", 
        "Litmos__Total_User_Program_Results__c", 
        "Litmos__User_Id__c", 
        "Litmos__lp_Completed_Percentage__c", 
        "Litmos__p_Completed_Percentage__c", 
        "Licences__c", 
        "Validation_Bypass__c", 
        "maps__AllowMapsExports__c", 
        "maps__BetaTester__c", 
        "maps__DefaultLatitude__c", 
        "maps__DefaultLongitude__c", 
        "maps__DefaultProximityRadius__c", 
        "maps__DefaultType__c", 
        "maps__DefaultZoomLevel__c", 
        "maps__DeviceId__c", 
        "maps__DeviceVendor__c", 
        "maps__EditMapsOrgWideQueries__c", 
        "maps__FinishedAdvRouteSetup__c", 
        "maps__MapsSetting__c", 
        "maps__MaxExportSize__c", 
        "maps__MaxQuerySize__c", 
        "maps__PreferredTypeOfMeasurement__c", 
        "maps__ReceiveBatchExceptionEmails__c", 
        "maps__TPApprover__c", 
        "maps__TestUserLookup__c", 
        "maps__Version__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_sked__resource__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-sked-resource-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/sked__resource__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_sked__resource__c(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'sked__Resource__c'
    # set the columns
    target_columns = [
        "Id", 
        "OwnerId", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "sked__Alias__c", 
        "sked__Auto_Schedule__c", 
        "sked__Category__c", 
        "sked__Country_Code__c", 
        "sked__Email__c", 
        "sked__GeoLocation__Latitude__s", 
        "sked__GeoLocation__Longitude__s", 
        "sked__Home_Address__c", 
        "sked__Is_Active__c", 
        "sked__Mobile_Phone__c", 
        "sked__Notes__c", 
        "sked__Notification_Type__c", 
        "sked__Primary_Phone__c", 
        "sked__Primary_Region__c", 
        "sked__Rating__c", 
        "sked__Resource_Type__c", 
        "sked__User__c", 
        "sked__Weekly_Hours__c", 
        "FTE__c", 
        "Level__c", 
        "Mobile_Phone__c", 
        "Manager__c", 
        "sked__Employment_Type__c", 
        "sked__Working_Hour_Type__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_sked__availability__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-sked-availability-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/sked__availability__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_sked__availability__c(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'sked__Availability__c'
    # set the columns
    target_columns = [
        "Id", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "sked__Resource__c", 
        "sked__Finish__c", 
        "sked__Is_Available__c", 
        "sked__Notes__c", 
        "sked__Start__c", 
        "sked__Status__c", 
        "sked__Timezone__c", 
        "sked__Type__c", 
        "Payrol_Calendar_Sync__c", 
        "Week_Cycle__c", 
        "Date__c", 
        "Days_of_Cycle__c", 
        "Day__c", 
        "Finish_Next_2_Weeks__c", 
        "Finish_Next_Rotation__c", 
        "Finish_Next_Week__c", 
        "Start_Next_2_Weeks__c", 
        "Start_Next_Rotation__c", 
        "Start_Next_Week__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_contact")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-contact",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/contact/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_contact(inputblobSession:str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Contact'
    # set the columns
    target_columns = [
        "Id", 
        "IsDeleted", 
        "MasterRecordId", 
        "AccountId", 
        "LastName", 
        "FirstName", 
        "Salutation", 
        "Name", 
        "OtherStreet", 
        "OtherCity", 
        "OtherState", 
        "OtherPostalCode", 
        "OtherCountry", 
        "OtherLatitude", 
        "OtherLongitude", 
        "OtherGeocodeAccuracy", 
        "MailingStreet", 
        "MailingCity", 
        "MailingState", 
        "MailingPostalCode", 
        "MailingCountry", 
        "MailingLatitude", 
        "MailingLongitude", 
        "MailingGeocodeAccuracy", 
        "Phone", 
        "Fax", 
        "MobilePhone", 
        "HomePhone", 
        "OtherPhone", 
        "AssistantPhone", 
        "ReportsToId", 
        "Email", 
        "Title", 
        "Department", 
        "AssistantName", 
        "LeadSource", 
        "Birthdate", 
        "Description", 
        "OwnerId", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastActivityDate", 
        "LastCURequestDate", 
        "LastCUUpdateDate", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "EmailBouncedReason", 
        "EmailBouncedDate", 
        "IsEmailBounced", 
        "PhotoUrl", 
        "Jigsaw", 
        "JigsawContactId", 
        "Main_Contact__c", 
        "Send_CDM_Letter__c", 
        "Phone_with_Country_Code__c", 
        "Mobile_with_Country_Code__c", 
        "Account_Manager_Name__c", 
        "Onboarding_Buddy__c", 
        "Courtesy_Email__c", 
        "CDM_Campaign_Letter_URL__c", 
        "NPS_Batch_Number__c", 
        "Key_Contact__c", 
        "Group_ID__c", 
        "Contact_For__c", 
        "Active__c", 
        "Podiatry_Handover__c", 
        "Medicare__c", 
        "Survey__c", 
        "Marketing__c", 
        "TIMBASURVEYS__SurveyReminder__c", 
        "TIMBASURVEYS__Survey__c", 
        "TIMBASURVEYS__reminderStringSize__c", 
        "Contact_Type_Id__c", 
        "Role__c", 
        "Survey_Due_Date__c", 
        "Last_NPS_Score__c", 
        "Survey_Reminder_2__c", 
        "Survey_Reminder_1__c", 
        "Survey_Reminder_1_String__c", 
        "Survey_Reminder_2_String__c", 
        "Client__c", 
        "CDM_Campaign_Opt_In__c", 
        "CDM_Campaign_Opt_Out__c", 
        "Survey_Sent_Date__c", 
        "User__c", 
        "Date_of_Last_Activity__c", 
        "Additional_notes__c", 
        "G2Latitude__c", 
        "G2Longitude__c", 
        "G2GeoStatus__c", 
        "Contact_Facility_Name__c", 
        "Bypass__c", 
        "Last_NPS_Date__c", 
        "Key_Medicare_Contact__c", 
        "Last_NPS_Score_Actual__c", 
        "NPS_Response_Last_7_Days__c", 
        "Start_Date__c", 
        "First_NPS_Score__c", 
        "Most_Recent_NPS_Response__c", 
        "NPS_Repeat_Responder__c", 
        "Responded_To_Survey__c", 
        "Contact_ID_18ch__c", 
        "Survey_Opt_Out__c", 
        "Skip_survey_reminder__c", 
        "sked__Region__c", 
        "NPS_A_B_Testing_Group__c", 
        "Campaign_Opt_In_Notes__c", 
        "Bounced_Email__c", 
        "Contact_Type__c", 
        "Address_1__c", 
        "Address_2__c", 
        "Address_3__c", 
        "City__c", 
        "Company_Name__c", 
        "Clinic_Name__c", 
        "Patient_Id__c", 
        "Clinic_Location__c", 
        "Appointment_End__c", 
        "Appointment_Start__c", 
        "Appointment_Length__c", 
        "Appointment_Time__c", 
        "Appointment_Date__c", 
        "Cancellation_Time__c", 
        "Appointment_Cancelled__c", 
        "Patient_Arrived__c", 
        "Cliniko_Patient_ID__c", 
        "Sex__c", 
        "Postcode__c", 
        "Marketing_Cloud_Sync__c", 
        "PPMP_Patient_ID__c", 
        "Next_Birthday__c", 
        "Age__c", 
        "Age_Demographic__c", 
        "Last_Appointment__c", 
        "Lapsed__c", 
        "Date_Last_Seen__c", 
        "Total_Number_of_Appointments__c", 
        "Funder__c", 
        "Hours_of_Service_per_Fortnight__c", 
        "Litmos__Access_Level__c", 
        "Litmos__Completed_Percentage__c", 
        "Litmos__Courses_Assigned__c", 
        "Litmos__Courses_Completed__c", 
        "Litmos__Deactivate_From_Litmos__c", 
        "Litmos__Full_Name__c", 
        "Litmos__Languages__c", 
        "Litmos__Level__c", 
        "Litmos__LitmosID__c", 
        "Litmos__Litmos_Activated__c", 
        "Litmos__Litmos_Login_Access__c", 
        "Litmos__Litmos_UserId__c", 
        "Litmos__OriginalId__c", 
        "Litmos__Sync_Litmos__c", 
        "Litmos__Total_Sum_Percentages__c", 
        "Litmos__User_Id__c", 
        "Litmos__p_Completed_Percentage__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_account")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-account",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/account/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_account(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Account'
    # set the columns
    target_columns = [
        "Id", 
        "IsDeleted", 
        "MasterRecordId", 
        "Name", 
        "Type", 
        "RecordTypeId", 
        "ParentId", 
        "BillingStreet", 
        "BillingCity", 
        "BillingState", 
        "BillingPostalCode", 
        "BillingCountry", 
        "BillingLatitude", 
        "BillingLongitude", 
        "BillingGeocodeAccuracy", 
        "ShippingStreet", 
        "ShippingCity", 
        "ShippingState", 
        "ShippingPostalCode", 
        "ShippingCountry", 
        "ShippingLatitude", 
        "ShippingLongitude", 
        "ShippingGeocodeAccuracy", 
        "Phone", 
        "Fax", 
        "AccountNumber", 
        "Website", 
        "PhotoUrl", 
        "Sic", 
        "Industry", 
        "AnnualRevenue", 
        "NumberOfEmployees", 
        "Ownership", 
        "TickerSymbol", 
        "Description", 
        "Rating", 
        "Site", 
        "OwnerId", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastActivityDate", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "IsCustomerPortal", 
        "Jigsaw", 
        "JigsawCompanyId", 
        "AccountSource", 
        "SicDesc", 
        "No_of_Beds__c", 
        "High_Care__c", 
        "Low_Care__c", 
        "Numbers_to_Treat__c", 
        "Metro__c", 
        "Group_Name__c", 
        "Distance_from_City__c", 
        "Caller_s_Name__c", 
        "Date_of_Next_CPI_Increase__c", 
        "Average_Treatment_Numbers__c", 
        "Email__c", 
        "Facility_Notes_2__c", 
        "Date_Lost__c", 
        "Current_ESA_Expiry__c", 
        "Quality_Check_date__c", 
        "Quality_Check_Notes__c", 
        "Any_actions_from_Quality_Check__c", 
        "Survey_Notes__c", 
        "High_Care_Fee__c", 
        "Low_Care_Fee__c", 
        "Low_Care_Fee_Invoice__c", 
        "ESA_Sent__c", 
        "Resident_listing_recd__c", 
        "Start_Up_pack_sent__c", 
        "Date_couriered_Att_To__c", 
        "Start_Date__c", 
        "Start_Up_Notes__c", 
        "Creation_Date_Facility__c", 
        "X4T_education_done__c", 
        "Dimple_Podiatrist_State__c", 
        "Group_Parent__c", 
        "Neurovascular_Assessment_Fee__c", 
        "Zone__c", 
        "ESA_Received__c", 
        "ESA_group_individual__c", 
        "Medicare_Report_details__c", 
        "Estimated_Annual_Return__c", 
        "Lost_Contract_Reason__c", 
        "Prospect_Status__c", 
        "Not_Interested_Reason__c", 
        "Prospect_Source__c", 
        "Facility_Notes__c", 
        "X4T_Done__c", 
        "Clinic_ID__c", 
        "Podiatrist_Changed_Date__c", 
        "Loyalty_Zone_results_Feb__c", 
        "Loyalty_Zone_results_2010_Q_2__c", 
        "Old_High_Care_Fee__c", 
        "Old_Low_Care_Fee__c", 
        "Date_of_Last_Fee_Increase__c", 
        "contact__c", 
        "Accommodation_details__c", 
        "Medicare_Reports_required__c", 
        "Community_Pt_Fee__c", 
        "Medicare_EPC_Fee__c", 
        "DVA_Fee__c", 
        "Customer_Type__c", 
        "Facility_billed_for_Low_Cares__c", 
        "Emergency_Fee__c", 
        "ESA_Notes__c", 
        "Competitor_info__c", 
        "Dimple_Podiatrist_sked__c", 
        "expiry__c", 
        "Competitors__c", 
        "Regional_Area__c", 
        "Accounts_Notes_on_Fees__c", 
        "Contacted_re_EPC__c", 
        "EPC_communication__c", 
        "Potential_EPC_Revenue__c", 
        "Community_Fee__c", 
        "Supplier_type__c", 
        "Invoice_EPC_DVA_comments__c", 
        "Managing_State__c", 
        "Queensland_LGA__c", 
        "Apartment_Number__c", 
        "Decision_level__c", 
        "New_High_Care_Fee__c", 
        "New_ESA_Expiry__c", 
        "Current_Campaign__c", 
        "New_Care_Plan_Fee__c", 
        "Current_Campaign_Visible__c", 
        "G2Latitude__c", 
        "G2Longitude__c", 
        "G2GeoStatus__c", 
        "Parent_Facility_Name__c", 
        "Reason_For_Excluded_Facility__c", 
        "TCP_Fee__c", 
        "Exclude_from_EPC_Reporting__c", 
        "Size_SQM__c", 
        "State_and_Zone__c", 
        "ffbf__AccountParticulars__c", 
        "ffbf__BankBIC__c", 
        "ffbf__PaymentCode__c", 
        "ffbf__PaymentCountryISO__c", 
        "ffbf__PaymentPriority__c", 
        "ffbf__PaymentRoutingMethod__c", 
        "Private_and_Confidential__c", 
        "Agreed_Minimum_Fee__c", 
        "Next_of_Kin__c", 
        "Next_of_Kin_Details__c", 
        "Credit_Card_Type__c", 
        "Credit_Card_Number__c", 
        "Credit_Card_Expiry_Date__c", 
        "Expected_Start_Date__c", 
        "Flat_Fee__c", 
        "Facility_Notes_3__c", 
        "Wing_Names__c", 
        "Facility_Name_FF__c", 
        "Session_Profit__c", 
        "of_EPC_Referrals_Left__c", 
        "Not_for_Profit__c", 
        "Kane_Question_Answers__c", 
        "Income__c", 
        "Minimum_Fee_Structure__c", 
        "Minimum_Fee__c", 
        "Patients_DO_NOT_TREAT__c", 
        "Total_Income_Last_2_Quarters__c", 
        "Total_Treatments_Last_2_Quarters__c", 
        "No_of_Fill_In_Sessions_Last_180_Days__c", 
        "Total_Completed_Session_Count__c", 
        "No_of_Fill_In_Sessions__c", 
        "Total_Session_Count_Last_180_Days__c", 
        "New_Facility__c", 
        "Billing_Name__c", 
        "Patient_Care_Level__c", 
        "No_of_Facilities__c", 
        "Total_No_of_Beds__c", 
        "Next_Session__c", 
        "Number_of_Days_til_Next_Event__c", 
        "Next_Podiatry_Session_Date__c", 
        "Number_of_Days_til_Next_Session__c", 
        "Facility_Start_Month__c", 
        "Handover_Email_ID__c", 
        "Handover_Email_CC__c", 
        "Recent_Podiatrists__c", 
        "Start_Time__c", 
        "Door_Code__c", 
        "Privacy_Screen__c", 
        "Treatment_Room__c", 
        "Notes_System__c", 
        "Username__c", 
        "Password__c", 
        "Minimum_Fee_Notes__c", 
        "Door_Code_Wings__c", 
        "Location_of_Treatment_Room__c", 
        "Car_Parking_Details__c", 
        "Physical_Full_Address__c", 
        "Active__c", 
        "No_of_Facilities_Not_Serviced__c", 
        "Not_Treated_List__c", 
        "Single_Site_NPS__c", 
        "No_Current_Customers__c", 
        "Parent_Roll_Up_CDM_Savings__c", 
        "Parent_Roll_Up_HC_Spend__c", 
        "Parent_Roll_Up_HC_Tx__c", 
        "Parent_Roll_Up_CDM_Tx__c", 
        "Parent_Roll_Up_Total_Tx__c", 
        "MALatitude__c", 
        "MALongitude__c", 
        "MACleanPostalCode__c", 
        "MAVerifiedLatitude__c", 
        "MACleanCounty__c", 
        "MACleanCity__c", 
        "MAVerifiedLongitude__c", 
        "MACleanCountry__c", 
        "MASimilarity__c", 
        "MACleanState__c", 
        "MACleanStreet__c", 
        "MASkipGeocoding__c", 
        "MACleanDistrict__c", 
        "MAQuality__c", 
        "Group_Statement_URL__c", 
        "Receipt_Required__c", 
        "Opt_Out_CDM_letter_no_email__c", 
        "Handover_Email__c", 
        "Handover_Email_CC_Trim__c", 
        "Facility_Communications_CC_1__c", 
        "Facility_Communications_CC_2__c", 
        "Facility_Communications_CC_3__c", 
        "Facility_Communications_CC_4__c", 
        "Facility_Communications_CC_5__c", 
        "Podiatry_Handover_Email_CC_Conga__c", 
        "Dimple_Podiatrist2__c", 
        "Group_ID__c", 
        "CongaState__c", 
        "Major_City_Area__c", 
        "Statistical_Region__c", 
        "Total_Session_Count__c", 
        "CPI_Increase_Agreed__c", 
        "Total_High_Care_Tx_Last_12_Months__c", 
        "General_Region__c", 
        "Total_Income_Last_12_Months__c", 
        "Total_CDM_Treatments_last_12_months__c", 
        "Number_of_Sites__c", 
        "Total_CDM_Savings_last_12_months_c__c", 
        "Total_Treatments_Last_12_Months__c", 
        "Total_High_Care_Spend_Last_12_Months__c", 
        "ILU__c", 
        "Percent_CDM_Tx_Last_12_Months__c", 
        "Parent_Net_Fee__c", 
        "Net_Fee_Lst_12_Months__c", 
        "Promoters__c", 
        "Handover_Report_Preference__c", 
        "Parent_Count_Sites_without_CDM_Referrals__c", 
        "Parent_Count_Sites_with_CDM_Referrals__c", 
        "Percentage_of_treatments__c", 
        "Percentage_of_CDM_treatments_sites_w_CDM__c", 
        "Total_Revenue_12_months_before__c", 
        "NPS_Group__c", 
        "Unsuitable_Podiatry_Days__c", 
        "Group_Name_Trim__c", 
        "Parent_Roll_Up_Percent_CDM__c", 
        "Parent_Roll_up_with_CDM_Total_Treatmen__c", 
        "Parent_Roll_up_w_CDM_percent_CDM__c", 
        "Parent_Roll_up_sites_w_o_CDM_Total_Tx__c", 
        "No_Oboarding_c__c", 
        "Potential_Savings_20_pc__c", 
        "Percent_of_Residents_Treated_Each_6_Week__c", 
        "NPS_Responses_Last_180_days__c", 
        "Promoters_NPS_Responses_Last_180_days__c", 
        "Total_Detractors_NPS_Last_180_days__c", 
        "Parent_Roll_Up_NPS_Responses__c", 
        "Parent_Roll_Up_NPS_Promoters__c", 
        "Parent_Roll_Up_NPS_Detractors__c", 
        "Parent_NPS_Score__c", 
        "Client_Segment__c", 
        "Start_of_Group_Relationship__c", 
        "Group_Cluster__c", 
        "Count_Active_Patients_w_o_CDM_Referrals__c", 
        "Count_Active_Patients_Due_CDM_Referrals__c", 
        "Referrals_Due_Potential_Savings__c", 
        "Residents_no_Referrals_Potential_Saving__c", 
        "Total_residents_without_referrals__c", 
        "Total_Potential_Savings__c", 
        "Servicing_Region__c", 
        "Roll_up_session_profit__c", 
        "Client__c", 
        "Podiatry_Handover_Email_1__c", 
        "Documentation_Type__c", 
        "Door_Code_Nurses_Station__c", 
        "Podiatry_Handover_Email_2__c", 
        "Test_HC_Contract_Fee__c", 
        "Test_LC_Contract_Fee__c", 
        "Test_Minimum_Fee__c", 
        "Treatments_Per_Cycle__c", 
        "referrals_due_for_renew__c", 
        "Recent_Continuity__c", 
        "Send_Statement__c", 
        "Tx_every_6_Weeks__c", 
        "Date_of_Last_Session__c", 
        "Last_Service_Date__c", 
        "Test_Emergency__c", 
        "Test_Community__c", 
        "Test_TCP__c", 
        "Test_NCP__c", 
        "Test_Flat_Fee__c", 
        "Test_Date_of_Next_CPI_Inrease__c", 
        "Test_Current_ESA_Expiry__c", 
        "Test_ESA_Type__c", 
        "CPI_Increase_Ammount__c", 
        "Podiatry_Handover_Email_3__c", 
        "Part_of_Group_We_Service__c", 
        "ClientName__c", 
        "Number_of_DVA_Eligible_Residents__c", 
        "Eligible_DVA_Resident_List__c", 
        "Number_of_Residents_with_Missing_CDM_Inf__c", 
        "List_of_CDM_Residents_Missing_DOB__c", 
        "List_of_CDM_Res_Missing_MC_numbers__c", 
        "List_of_CDM_Residents_Ref_Date__c", 
        "Podiatry_Handover_Email_4__c", 
        "Parent_NPS__c", 
        "States_Serviced_By_Group__c", 
        "State__c", 
        "Parent_Total_Beds_Serviced_By_Dimpe__c", 
        "Current_Client__c", 
        "Percentage_of_Beds_Serviced_by_Dimple__c", 
        "Parent_Total_Income_Last_12_Months__c", 
        "Parent_Beds_Greater_Than_12_Months_Old__c", 
        "Start_Less_Than_Last_365__c", 
        "Parent_Total_Income_Sites_Older_Than_1yr__c", 
        "Parent_Beds_Serviced_Greater_than_12mo__c", 
        "Parent_Revenue_Per_Bed__c", 
        "Facility_Information__c", 
        "Bypass__c", 
        "Podiatry_Handover_Email_5__c", 
        "States_Serviced_By_PArent__c", 
        "Need_to_Know__c", 
        "Podiatry_Handover_Email_6__c", 
        "Podiatry_Handover_Email_7__c", 
        "Number_of_Regular_Pods__c", 
        "of_Cover_Sessions__c", 
        "of_Sessions__c", 
        "x12_Month_Continuity__c", 
        "Parent_Start_Date__c", 
        "Number_of_Complaints_or_Concerns__c", 
        "Active_Contract_Signed__c", 
        "Active_Contract_Waiting_Start_Date__c", 
        "Active_Contract_Not_Signed__c", 
        "Contract_Status__c", 
        "Podiatry_Handover_Email_8__c", 
        "Podiatry_Handover_Email_9__c", 
        "Podiatry_Handover_Email_10__c", 
        "Courtesy_Email_1__c", 
        "Scheduling_Information__c", 
        "Courtesy_Email_2__c", 
        "Courtesy_Email_3__c", 
        "Courtesy_Email_4__c", 
        "Courtesy_Email_5__c", 
        "Courtesy_Email_6__c", 
        "Courtesy_Email_7__c", 
        "Courtesy_Email_8__c", 
        "Courtesy_Email_9__c", 
        "Courtesy_Email_10__c", 
        "CDM_Campaign_Opt_In_Email_1__c", 
        "CDM_Campaign_Opt_In_Email_2__c", 
        "CDM_Campaign_Opt_In_Email_3__c", 
        "CDM_Campaign_Opt_In_Email_4__c", 
        "CDM_Campaign_Opt_In_Email_5__c", 
        "CDM_Campaign_Opt_In_Email_6__c", 
        "CDM_Campaign_Opt_In_Email_7__c", 
        "CDM_Campaign_Opt_In_Email_8__c", 
        "CDM_Campaign_Opt_In_Email_9__c", 
        "CDM_Campaign_Opt_In_Email_10__c", 
        "Main_Contact__c", 
        "Number_of_Facility_Manager_Roles__c", 
        "Quality_Requirements__c", 
        "Dpod__c", 
        "Contract_Connection_Count__c", 
        "CDM_Campaign_Letter_URL__c", 
        "CDM_Campaign_CC_Conga__c", 
        "CDM_Campaign_CC_Conga_Trim__c", 
        "Main_Contact_First_Name__c", 
        "Last_CDM_Campaign_Sent__c", 
        "Tableau_Customer_Segment__c", 
        "Team_Manager__c", 
        "Mass_Generate_CDM_Reports_URL__c", 
        "Tableau_Podiatry_Team__c", 
        "Date_LC_Account_Was_Last_Seen__c", 
        "Number_of_Overdue_Invoices__c", 
        "Send_Statement_URL__c", 
        "Date_LC_Statement_Was_Last_Sent__c", 
        "LC_Account_First_Name__c", 
        "Compliance_Requirements__c", 
        "Induction_System__c", 
        "Education_Requirements__c", 
        "Quality_Review_Period__c", 
        "Documentation_Process__c", 
        "Number_of_Patients_Related_To_LC_Acc__c", 
        "Last_Campaign__c", 
        "X3_Monthly_Evaluation_Complete__c", 
        "Lookup_to_Parent_Number_o_Facilities__c", 
        "Date_of_Last_AM_Visit__c", 
        "Hold_CDM_Email__c", 
        "Notes_Regarding_CDM_Reporting_Preference__c", 
        "Contract_Connection_Counter__c", 
        "Current_Contract_Connection__c", 
        "Number_of_CDM_Cases_Awaiting_Information__c", 
        "Lookup_To_Parent_Beds_Serviced_By_Dimple__c", 
        "Contract_Start_Date__c", 
        "Average_Accomodation_Per_Session__c", 
        "Avg_Allowance_per_session__c", 
        "Number_of_Sessions_Last_12_Months__c", 
        "Total_Incentives_Paid_Last_12_Months__c", 
        "of_Times_Hit_With_Campaign__c", 
        "Last_Parent_Campaign__c", 
        "Date_of_Last_Opportunity_Close__c", 
        "Overall_Date_of_Last_Campaign__c", 
        "Annual_Care_Plan_and_Assesment_Complete__c", 
        "sked__Rank__c", 
        "sked__Requires_Whitelist__c", 
        "Date_at_End_of_Current_Quarter__c", 
        "Start_of_Relationship__c", 
        "Number_of_Active_Contracts__c", 
        "AM__c", 
        "Date_of_Last_Campaign_Response__c", 
        "Account_Manager__c", 
        "Emergency_Fee_Non_CDM__c", 
        "Emergency_Fee_CDM__c", 
        "Status__c", 
        "Problems_Cases_Last_12_Months__c", 
        "Days_Since_Start_Date__c", 
        "Main_Contact_ID__c", 
        "Total_Treatments_Previous_12_Months__c", 
        "Total_Treatments_36_48_Months_Ago__c", 
        "Last_Known_Competitor_Fee__c", 
        "Competitor_Notes__c", 
        "Last_Campaign_Response__c", 
        "Last_Campaign_Notes__c", 
        "Exclude_From_Pod_Tier_Average__c", 
        "Number_of_Active_Contract_Connections__c", 
        "Contract_Linked_to_Contract_Connection__c", 
        "Number_of_CDM_Residents_Without_DOBs__c", 
        "Last_Job_Date__c", 
        "Current_Opportunity_Connection__c", 
        "Current_Contract_Connection2__c", 
        "Number_of_Open_Opportunity_Connections__c", 
        "Current_Contract_Number_Temp__c", 
        "Contract_Text__c", 
        "Excluded_Reason_Vetted__c", 
        "Dimple_Podiatrist_Lat__c", 
        "Offboarding__c", 
        "Dimple_Podiatrist_Long__c", 
        "Dimple_Podiatrist_Postcode__c", 
        "AH_Clinic_Status__c", 
        "Practice_Code__c", 
        "Origin__c", 
        "Destination__c", 
        "Lat_Text__c", 
        "Long_Text__c", 
        "Potential_Savings_20pc_W_Referrals__c", 
        "Parent_Facilitty_Type__c", 
        "Number_of_Consulting_Rooms_Beds__c", 
        "Total_Operating_Hours__c", 
        "Total_Consulting_Capacity__c", 
        "Pilates_Studio_Gym__c", 
        "Weekday_Hours__c", 
        "PPMP_Clinic_ID__c", 
        "Physio_Provider__c", 
        "Schedule_Rotation__c", 
        "Facility_Statement_URL__c", 
        "PPMP_Clinic_ID_Text__c", 
        "Medicare_Information_Email__c", 
        "Receipts_URL__c", 
        "Total_Community_Clients__c", 
        "Number_of_HCP_Clients__c", 
        "Number_of_NDIS_Clients__c", 
        "Medicare_Rejection_URL__c", 
        "Litmos__Active__c", 
        "Litmos__CustomerPriority__c", 
        "Litmos__Litmos_Id__c", 
        "Litmos__NumberofLocations__c", 
        "Litmos__SLAExpirationDate__c", 
        "Litmos__SLASerialNumber__c", 
        "Litmos__SLA__c", 
        "Litmos__UpsellOpportunity__c", 
        "BPAY_Direct_Debit_International__c", 
        "LC_HC_Statement_Send_URL__c", 
        "Lost_Facility__c", 
        "X18_CHAR_ID__c", 
        "maps__AssignmentRule__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_sked__job__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-sked-job-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/sked__job__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_sked__job__c(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'sked__Job__c'
    # set the columns
    target_columns = [
        "Id", 
        "OwnerId", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastActivityDate", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "sked__Abort_Reason__c", 
        "sked__Account__c", 
        "sked__Actual_End__c", 
        "sked__Actual_Start__c", 
        "sked__Address__c", 
        "sked__Auto_Schedule__c", 
        "sked__Can_Be_Declined__c", 
        "sked__Completion_Notes__c", 
        "sked__Contact__c", 
        "sked__Customer_Job_No__c", 
        "sked__Description__c", 
        "sked__Dispatch_At_Time__c", 
        "sked__Duration__c", 
        "sked__Estimated_End__c", 
        "sked__Estimated_Start__c", 
        "sked__Finish__c", 
        "sked__Follow_up_Reason__c", 
        "sked__GeoLocation__Latitude__s", 
        "sked__GeoLocation__Longitude__s", 
        "sked__Job_Status__c", 
        "sked__Location__c", 
        "sked__Locked__c", 
        "sked__Notes_Comments__c", 
        "sked__NotifyPeriod__c", 
        "sked__Notify_By__c", 
        "sked__Parent__c", 
        "sked__Recurring_Schedule__c", 
        "sked__Region__c", 
        "sked__Start__c", 
        "sked__Timezone__c", 
        "sked__Type__c", 
        "sked__Urgency__c", 
        "sked__Job_Allocation_Count__c", 
        "sked__Resource_Hours_Worked__c", 
        "of_Sharing_Session_Day__c", 
        "Reason_Rescheduled__c", 
        "Account_ID__c", 
        "Account_Parent_Name__c", 
        "Message_to_Podiatrist__c", 
        "Allowance_Type__c", 
        "Day__c", 
        "Date__c", 
        "Days_of_Cycle__c", 
        "Do_Not_Create_Session__c", 
        "Facility_Lockdown__c", 
        "Length_of_Service__c", 
        "Notes_for_Accounts__c", 
        "Number_of_Related_Events__c", 
        "Permanent_Podiatrist_Change__c", 
        "Podiatry_Session_Scheduled_C_D__c", 
        "Podiatrist_Coverage_Type__c", 
        "Rooms_1__c", 
        "Rooms_2__c", 
        "Scheduling_Information__c", 
        "Session__c", 
        "Session_Coverage_Type__c", 
        "Session_ID__c", 
        "Session_Name__c", 
        "Session_Percentage_of_Day__c", 
        "Session_Type__c", 
        "Unsuitable_Days__c", 
        "Week_Cycle__c", 
        "X12_Month_Continuity__c", 
        "Wing_1__c", 
        "Wing_2__c", 
        "Wing_3__c", 
        "Wing_4__c", 
        "Wing_5__c", 
        "Wing_6__c", 
        "Wing_7__c", 
        "Wing_8__c", 
        "Wing_9__c", 
        "Original_Date__c", 
        "Scheduling_Notes__c", 
        "Label__c", 
        "Next_Service_Date__c", 
        "Resource_User_ID__c", 
        "Next_Job_Date__c", 
        "Total_Treatments__c", 
        "Total_Income__c", 
        "Total_CDM_Treatments__c", 
        "Job_ID_Long__c", 
        "Resource_Name__c", 
        "Week_Gap_to_Next_Job__c", 
        "Regular_Podiatrist__c", 
        "Resource_ID__c", 
        "Scheduling_Task__c", 
        "Date_Task__c", 
        "Account_Parent_ID__c", 
        "sked__Quantity__c", 
        "sked__Job_Allocation_Time_Source__c", 
        "sked__Resource_Requirement_Count__c", 
        "sked__Customer_Confirmation_Status__c", 
        "sked__Is_Group_Event__c", 
        "sked__Max_Attendees__c", 
        "sked__Min_Attendees__c", 
        "sked__Copied_From_Id__c", 
        "sked__Virtual_Meeting_Id__c", 
        "sked__Virtual_Meeting_Info__c", 
        "sked__Virtual_Meeting_URL__c", 
        "sked__Schedule_Template__c", 
        "sked__Templated_Job__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_session__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-session-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/session__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_session__c(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'Session__c'
    # set the columns
    target_columns = [
        "Id",
        "Claimable_Km_s__c",
        "Date__c",
        "Facility__c",
        "Number_of_Hours__c",
        "Address__c",
        "Total_Cost_For_Session__c",
        "Facility_billed_for_Low_Cares__c",
        "Total_Treatments__c",
        "Time_Onsite__c",
        "Hours_Worked__c",
        "Session_Facility_State__c",
        "Session_Facility_City__c",
        "Session_Owner_Name__c",
        "Treated_Patient_Names__c",
        "Medicare_EPC_Credit__c",
        "Billable_Treatments__c",
        "Total_Income_Formula__c",
        "Parent_Facility_Name__c",
        "Total_Income__c",
        "Facility_Name__c",
        "Distance_from_Home__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

@app.function_name(name="func_salesforce_dimple_export_sked__region__c")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="salesforce-dimple-trigger-sked-region-c",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="salesforce-dimple", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="salesforce-dimple/sked__region__c/api_ingest_{DateTime}_pp_{QueueTrigger}.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobSession",
                path="salesforce-dimple-session/session.txt",
                connection="AzureWebJobsStorage")
def func_salesforce_dimple_export_sked__region__c(inputblobSession: str, msgin: func.QueueMessage, outputblob: func.Out[str], msgout: func.Out[str]) -> func.HttpResponse:
    # set the object name
    target_endpoint = 'sked__Region__c'
    # set the columns
    target_columns = [
        "Id", 
        "OwnerId", 
        "IsDeleted", 
        "Name", 
        "CreatedDate", 
        "CreatedById", 
        "LastModifiedDate", 
        "LastModifiedById", 
        "SystemModstamp", 
        "LastViewedDate", 
        "LastReferencedDate", 
        "sked__Country_Code__c", 
        "sked__Description__c", 
        "sked__Location__Latitude__s", 
        "sked__Location__Longitude__s", 
        "sked__Radius__c", 
        "sked__Timezone__c"
    ]
    # set the endpoint api warehouse and table name
    if inputblobSession is not None:
        session_id, instance = inputblobSession.split(' ')
        query_builder = salesforce_api_modules.SalesforceApi(session_id=session_id, instance=instance)
    else:
        query_builder = salesforce_api_modules.SalesforceApi(username=os.environ['salesforce_dimple_username'], password=os.environ['salesforce_dimple_password'])
        query_builder.renew_session()
    query_builder.connect()        
    # set the filter
    target_filter = msgin.get_body().decode('utf-8')
    logging.info(f"Target ingestion endpoint:{target_endpoint} with filter {target_filter}")
    # query the data
    resp = query_builder.get_objects(target_columns, target_endpoint, target_filter)
    # save to blobstorage
    if resp['totalSize'] > 0:
        outputblob.set(json.dumps(resp['records']))
        msgout.set(f"done: {resp['done']} - Salesforce Dimple {target_endpoint} - {resp['totalSize']} records")
    else:
        msgout.set(f"No record - Salesforce Dimple {target_endpoint} - {resp}")

##########################################################################################################
# Sharepoint Sub Functions
##########################################################################################################

@app.function_name(name="func_sharepoint_export_claro_wip_master_roster")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="sharepoint-trigger-claro-wip-master-roster",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="sharepoint", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="zenitas/claro_wip_master_roster/file_upload_{DateTime}_fn_{QueueTrigger}",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobdateClaroWipMasterRoster",
                path="zenitas-sharepoint-datetime-record/claro_wip_master_roster.txt",
                connection="AzureWebJobsStorage")
def func_sharepoint_export_claro_wip_master_roster(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobdateClaroWipMasterRoster: func.Out[str]) -> func.HttpResponse:
    # get authenticated
    ctx = sharepoint_api_modules._authenticate_web_sharepoint_session(
        os.environ['sharepoint_site_url'],
        os.environ['sharepoint_username'],
        os.environ['sharepoint_password']
    )
    if ctx:
        # get and recover the file url from msgin
        file_url = os.environ['sharepoint_folder_claro_wip_master_roster'] + msgin.get_body().decode('utf-8').replace('|','/')
        # download the file
        file_content = sharepoint_api_modules._download_file(ctx, file_url)
        if len(file_content) > 0:
            if file_content == '-1':
                outputblobdateClaroWipMasterRoster.set(dt.strftime(dt.today() - timedelta(days=10), '%Y-%m-%d %H:%M:%S'))
                msgout.set(f"Failed to download file {file_url}")
            else:
                # save to blob storage
                outputblob.set(file_content)
                msgout.set(f"File {file_url} downloaded and saved to blob storage zenitas/claro_wip_master_roster/")
    else:
        logging.info("Failed to authenticate")
        outputblobdateClaroWipMasterRoster.set(dt.strftime(dt.today() - timedelta(days=10), '%Y-%m-%d %H:%M:%S'))

@app.function_name(name="func_sharepoint_export_plena_kpi_target")
@app.queue_trigger(arg_name="msgin", 
                   queue_name="sharepoint-trigger-plena-kpi-target",
                   connection="AzureWebJobsStorage")
@app.queue_output(arg_name="msgout", 
                  queue_name="sharepoint", 
                  connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblob", 
                path="zenitas/plena_kpi_target/file_upload_{DateTime}_fn_{QueueTrigger}",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobdatePlenaKpiTarget",
                path="zenitas-sharepoint-datetime-record/plena_kpi_target.txt",
                connection="AzureWebJobsStorage")
def func_sharepoint_export_plena_kpi_target(outputblob: func.Out[str], msgout: func.Out[str], msgin: func.QueueMessage, outputblobdatePlenaKpiTarget: func.Out[str]) -> func.HttpResponse:
    # get authenticated
    ctx = sharepoint_api_modules._authenticate_web_sharepoint_session(
        os.environ['sharepoint_site_url'],
        os.environ['sharepoint_username'],
        os.environ['sharepoint_password']
    )
    if ctx:
        # get and recover the file url from msgin
        file_url = os.environ['sharepoint_folder_plena_kpi_target'] + msgin.get_body().decode('utf-8').replace('|','/')
        # download the file
        file_content = sharepoint_api_modules._download_file(ctx, file_url)
        if len(file_content) > 0:
            if file_content == '-1':
                outputblobdatePlenaKpiTarget.set(dt.strftime(dt.today() - timedelta(days=10), '%Y-%m-%d %H:%M:%S'))
                msgout.set(f"Failed to download file {file_url}")
            else:
                # save to blob storage
                outputblob.set(file_content)
                msgout.set(f"File {file_url} downloaded and saved to blob storage zenitas/plena_kpi_target/")
    else:
        logging.info("Failed to authenticate")
        outputblobdatePlenaKpiTarget.set(dt.strftime(dt.today() - timedelta(days=10), '%Y-%m-%d %H:%M:%S'))

##########################################################################################################
# Run result collection function that saves the result queue messages to files for easier troubleshooting
##########################################################################################################

@app.queue_trigger(arg_name="msgin", queue_name='livehire', connection='AzureWebJobsStorage')
@app.blob_output(arg_name="outputblob", path="livehire-run-results/{DateTime}_{Id}.txt", connection="AzureWebJobsStorage")
def func_livehire_run_results(msgin: func.QueueMessage, outputblob: func.Out[str]) -> func.HttpResponse:
    outputblob.set(msgin.get_body().decode('utf-8'))
    logging.info(f"Saved message to blob storage livehire-run-results")

@app.queue_trigger(arg_name="msgin", queue_name='salesforce-dimple', connection='AzureWebJobsStorage')
@app.blob_output(arg_name="outputblob", path="salesforce-dimple-run-results/{DateTime}_{Id}.txt", connection="AzureWebJobsStorage")
def func_salesforce_dimple_run_results(msgin: func.QueueMessage, outputblob: func.Out[str]) -> func.HttpResponse:
    outputblob.set(msgin.get_body().decode('utf-8'))
    logging.info(f"Saved message to blob storage salesforce-dimple-run-results")

@app.queue_trigger(arg_name="msgin", queue_name='salesforce-plena', connection='AzureWebJobsStorage')
@app.blob_output(arg_name="outputblob", path="salesforce-plena-run-results/{DateTime}_{Id}.txt", connection="AzureWebJobsStorage")
def func_salesforce_plena_run_results(msgin: func.QueueMessage, outputblob: func.Out[str]) -> func.HttpResponse:
    outputblob.set(msgin.get_body().decode('utf-8'))
    logging.info(f"Saved message to blob storage salesforce-plena-run-results")

@app.queue_trigger(arg_name="msgin", queue_name='techone', connection='AzureWebJobsStorage')
@app.blob_output(arg_name="outputblob", path="techone-run-results/{DateTime}_{Id}.txt", connection="AzureWebJobsStorage")
def func_techone_run_results(msgin: func.QueueMessage, outputblob: func.Out[str]) -> func.HttpResponse:
    outputblob.set(msgin.get_body().decode('utf-8'))
    logging.info(f"Saved message to blob storage techone-run-results")

@app.queue_trigger(arg_name="msgin", queue_name='sharepoint', connection='AzureWebJobsStorage')
@app.blob_output(arg_name="outputblob", path="sharepoint-run-results/{DateTime}_{Id}.txt", connection="AzureWebJobsStorage")
def func_sharepoint_run_results(msgin: func.QueueMessage, outputblob: func.Out[str]) -> func.HttpResponse:
    outputblob.set(msgin.get_body().decode('utf-8'))
    logging.info(f"Saved message to blob storage sharepoint-run-results")


##########################################################################################################
# HTTP Trigger Function
##########################################################################################################
# @app.function_name(name="func_http_trigger")
# @app.route(route="func_http_trigger")
# def func_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP func_http_trigger function processed a request.')

#     name = req.params.get('value')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('value')

#     initial_value: int = int(name)
#     doubled_value: int = alayacare_api_modules.double(initial_value)

#     if name:
#         return func.HttpResponse(
#             body=f"{initial_value} * 2 = {doubled_value}",
#             status_code=200
#         )
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a value in the query string or in the request body for a personalized response.",
#              status_code=200
#         )
    
# @app.function_name(name="func_alayacare_billable_item")
# @app.route(route="func_alayacare_billable_item")
# def func_alayacare_billable_item(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP func_alayacare_billable_item function processed a request.')
#     PAGE_SIZE = 10000
#     SUCCESSFUL_RATE_THRESHOLD = 0.8  # 95% of the records should be successfully inserted into Snowflake
#     logging.info(f"Paging size is set to {PAGE_SIZE}")
#     TARGET_COLUMN_SCHEMA = StructType([
#         StructField('activity_codes', StringType(), nullable=True), 
#         StructField('bill_code', StringType(), nullable=True), 
#         StructField('bill_code_id', LongType(), nullable=True), 
#         StructField('bill_rate_external_id', StringType(), nullable=True), 
#         StructField('bill_rate_guid', LongType(), nullable=True), 
#         StructField('bill_rate_id', LongType(), nullable=True), 
#         StructField('billing_frequency', LongType(), nullable=True), 
#         StructField('branch', StringType(), nullable=True), 
#         StructField('branch_id', LongType(), nullable=True), 
#         StructField('cancelled_code_id', StringType(), nullable=True), 
#         StructField('chris_fields', StringType(), nullable=True), 
#         StructField('client', StringType(), nullable=True), 
#         StructField('client_group_id', LongType(), nullable=True), 
#         StructField('client_id', StringType(), nullable=True), 
#         StructField('cob', LongType(), nullable=True), 
#         StructField('create_user_id', StringType(), nullable=True), 
#         StructField('created_at', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('decimal_units', StringType(), nullable=True), 
#         StructField('description', StringType(), nullable=True), 
#         StructField('employee', StringType(), nullable=True), 
#         StructField('employee_id', LongType(), nullable=True), 
#         StructField('end_at', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('gl_revenue_acc_account_id', LongType(), nullable=True), 
#         StructField('guid_to', LongType(), nullable=True), 
#         StructField('id', LongType(), nullable=False), 
#         StructField('invoice_items', StringType(), nullable=True), 
#         StructField('invoices', StringType(), nullable=True), 
#         StructField('is_copy', BooleanType(), nullable=True), 
#         StructField('is_holiday', BooleanType(), nullable=True), 
#         StructField('is_modified', BooleanType(), nullable=True), 
#         StructField('is_splittable', BooleanType(), nullable=True), 
#         StructField('lock_key', StringType(), nullable=True), 
#         StructField('master_invoice', StringType(), nullable=True), 
#         StructField('master_invoice_id', StringType(), nullable=True), 
#         StructField('original_bill_code_id', LongType(), nullable=True), 
#         StructField('original_end_date_time', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('original_quantity', DecimalType(38, 2), nullable=True), 
#         StructField('original_rate', DecimalType(38, 2), nullable=True), 
#         StructField('original_start_date_time', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('premium', StringType(), nullable=True), 
#         StructField('premium_id', StringType(), nullable=True), 
#         StructField('program', StringType(), nullable=True), 
#         StructField('program_id', LongType(), nullable=True), 
#         StructField('quantity', DecimalType(38, 2), nullable=True), 
#         StructField('rate', DecimalType(38, 2), nullable=True), 
#         StructField('rating_methodology', StringType(), nullable=True), 
#         StructField('service_code', StringType(), nullable=True), 
#         StructField('service_code_id', LongType(), nullable=True), 
#         StructField('source_id', LongType(), nullable=True), 
#         StructField('source_type', StringType(), nullable=True), 
#         StructField('start_at', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('status', StringType(), nullable=True), 
#         StructField('taxes', StringType(), nullable=True), 
#         StructField('tiered_units', StringType(), nullable=True), 
#         StructField('timezone', StringType(), nullable=True), 
#         StructField('unit', StringType(), nullable=True), 
#         StructField('update_user_id', LongType(), nullable=True), 
#         StructField('updated_at', TimestampType(TimestampTimeZone.TZ), nullable=True), 
#         StructField('value', DecimalType(38, 2), nullable=True), 
#         StructField('visit_id', LongType(), nullable=True), 
#         StructField('azure_insert_time', TimestampType(TimestampTimeZone.TZ), nullable=True)
#     ])

#     start_date = req.params.get('start_date')
#     # Validate the request parameters and return error if start_date is not following the format of YYYY-MM-DDTHH:MM:SSZ
#     if start_date:
#         try:
#             dt.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
#         except ValueError:
#             return func.HttpResponse(
#                 "Invalid start_date format. Please use YYYY-MM-DDTHH:MM:SSZ.",
#                 status_code=400
#             )
        
#     end_date = req.params.get('end_date')
#     # Validate the request parameters and return error if end_date is not following the format of YYYY-MM-DDTHH:MM:SSZ
#     if end_date:
#         try:
#             dt.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
#         except ValueError:
#             return func.HttpResponse(
#                 "Invalid end_date format. Please use YYYY-MM-DDTHH:MM:SSZ.",
#                 status_code=400
#             )

#     billable_item_query = alayacare_api_modules.AlayaCareDataQueryBillableItem(
#         username=os.environ['alayacare_username'],
#         password=os.environ['alayacare_password'],
#         url=os.environ['alayacare_endpoint_rating_billable_item'],
#         params=req.params
#     )

#     # Get the total relevant billable items count
#     try:
#         total_record_count = billable_item_query.get_total_billable_item_count()
#     except Exception as e:
#         logging.error(f"Error retrieving total billable item count: {e}")
#         return func.HttpResponse(
#             body=f"Error retrieving total billable item count: {e.args[0]['status_message'] if 'status_message' in e.args[0] else e}",
#             status_code=e.args[0]['status_code'] if 'status_code' in e.args[0] else 500
#         )
#     _total_pages_to_fetch = billable_item_query.calculate_pagination(total_items = total_record_count, count = PAGE_SIZE)
#     logging.info(f"Total records to fetch: {total_record_count}, Total pages to fetch: {_total_pages_to_fetch}")

#     # Iterate through the pages to retrieve all billable items
#     fetch_result = []
#     for page in range(1, _total_pages_to_fetch + 1):
#         this_result = {
#             "page": page,
#             "expected_size": min(PAGE_SIZE, total_record_count - (page - 1) * PAGE_SIZE),
#             "ac_status_code": None,
#             "ac_message": None,
#             "ac_record_count": 0,
#             "sf_status": None,
#             "sf_message": None,
#             "sf_record_count": 0
#         }
#         try:
#             retrieved_records = billable_item_query.get_list_of_billable_items(count = PAGE_SIZE, page = page)
#         except Exception as e:
#             logging.error(f"Error retrieving billable items page {page}: {e}")
#             this_result["ac_status_code"] = e.args[0]['status_code'] if 'status_code' in e.args[0] else 500
#             this_result["ac_message"] = f"Error retrieving billable items from page {page}: {e.args[0]['status_message'] if 'status_message' in e.args[0] else e}"
#         else:
#             # TO-DO
#             logging.info(f"Retrieved {len(retrieved_records)} records from page {page}.")
#             this_result["ac_status_code"] = 200
#             this_result["ac_message"] = f"Retrieved {len(retrieved_records)} billable items from page {page}."
#             this_result["ac_record_count"] = len(retrieved_records)
#             try:
#                 this_snowflake_result = snowflake_api_modules.insert_data_to_snowflake_table_with_schema_validation(
#                     retrieved_records,
#                     os.environ['snowflake_table_alayacare_billable_item'],
#                     TARGET_COLUMN_SCHEMA
#                 )
#             except Exception as e:
#                 logging.error(f"Error inserting data into Snowflake: {e}")
#                 this_result["sf_status"] = 'failed'
#                 this_result["sf_message"] = f"{e}"
#             else:
#                 logging.info(f"{this_snowflake_result['message'] if 'message' in this_snowflake_result else this_snowflake_result}")
#                 this_result["sf_status"] = this_snowflake_result['status'] if 'status' in this_snowflake_result else 'failed'
#                 this_result["sf_message"] = this_snowflake_result['message'] if 'message' in this_snowflake_result else 'No message provided'
#                 this_result["sf_record_count"] = this_snowflake_result['rows_inserted'] if 'rows_inserted' in this_snowflake_result else 0
#         fetch_result.append(this_result)

#     # get the total ac record counts and total sf record counts from fetch_result
#     if len(fetch_result) > 0:
#         ac_record_counts = [result["ac_record_count"] for result in fetch_result]
#         if sum(ac_record_counts) >= total_record_count * SUCCESSFUL_RATE_THRESHOLD:
#             most_frequent_ac_status_code = 200
#         else:
#             # get the most frequent ac status code that is not 200 from fetch_result
#             ac_status_codes = [result["ac_status_code"] for result in fetch_result if result["ac_status_code"] != 200]
#             if ac_status_codes:
#                 most_frequent_ac_status_code = max(set(ac_status_codes), key=ac_status_codes.count)
#             else:
#                 most_frequent_ac_status_code = 403
#         sf_record_counts = [result["sf_record_count"] for result in fetch_result]
#         if sum(sf_record_counts) >= total_record_count * SUCCESSFUL_RATE_THRESHOLD:
#             most_frequent_sf_status = 'success'
#         else:
#             most_frequent_sf_status = 'failed'
#     else:
#         # this means no records were found at all
#         logging.warning("No records were found from AlayaCare API.")
#         most_frequent_ac_status_code = 404
#         most_frequent_sf_status = 'skipped'
    
#     # to-do decide if should run curation proc in snowflake
#     snowflake_curation_procedure_result = {
#         'message': 'curation procedure not called',
#         'status': 'skipped',
#         'total_records_curated': 0
#     }
#     if most_frequent_ac_status_code == 200 and most_frequent_sf_status == 'success':
#         logging.info("All pages fetched successfully and most records are inserted into Snowflake. Running curation procedure.")
#         # only in this situation we can run the curation procedure
#         try:
#             call_result = snowflake_api_modules.call_stored_procedure(
#                 os.environ['snowflake_curated_sp_alayacare_billable_item']
#             )
#         except Exception as e:
#             logging.error(f"Error executing curation procedure: {e}")
#             snowflake_curation_procedure_result["message"] = f"Error executing curation procedure: {e.args[0]}"
#             snowflake_curation_procedure_result["status"] = 'failed'
#             over_all_status_code = 503
#         else:
#             logging.info("Curation procedure executed successfully.")
#             snowflake_curation_procedure_result = call_result
#             logging.info(f"Curation procedure result: {snowflake_curation_procedure_result}")
#             overall_status_code = 200
#     elif most_frequent_ac_status_code != 200 and most_frequent_sf_status != 'success':
#         logging.error(f"Some pages failed to fetch from AlayaCare API and failed to be inserted into Snowflake. Most frequent ac status code: {most_frequent_ac_status_code}. Most frequent sf status: {most_frequent_sf_status}")
#         overall_status_code = 503
#     else:
#         logging.warning(f"All pages fetched successfully but some pages failed to insert into Snowflake. Most frequent sf status: {most_frequent_sf_status}")
#         overall_status_code = 503


#     return func.HttpResponse(
#         body=json.dumps({
#             'ingestion': fetch_result,
#             'snowflake_curation_procedure': snowflake_curation_procedure_result
#         }),
#         status_code=overall_status_code
#     )
