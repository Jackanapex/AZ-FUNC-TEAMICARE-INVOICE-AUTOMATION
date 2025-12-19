import logging

import azure.functions as func
import os
import json
from datetime import datetime as dt
from datetime import timedelta

from this_app_module import splose_api_modules
from this_app_module import myob_api_modules

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# @app.function_name(name="func_a_simple_one")
# @app.route(route="func_a_simple_one", methods=["GET"])
# def func_a_simple_one(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info("func_a_simple_one called.")
#     return func.HttpResponse("Hello from func_a_simple_one!", status_code=200)

# @app.blob_input(arg_name="inputblob",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobAccessToken",
#                 path="teamicare/myob_authorize/access_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobRefreshToken",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
def func_myob_authorize(inputblob: str, outputblobAccessToken: func.Out[str], outputblobRefreshToken: func.Out[str]) -> dict:
    logging.info("Starting MYOB authorization process...")
    try:
        refreshed_result = myob_api_modules.refresh_access_token(
            os.environ["myob_authorize_url"],
            os.environ["myob_client_id"],
            os.environ["myob_client_secret"],
            inputblob
        )
    # when the refresh is failed, start from getting authorization code
    except Exception as e:
        logging.error(f"Failed to refresh MYOB access token: {e}, starting from authentication code")
        # if refresh token fails, start from getting authorization code
        access_code_url = myob_api_modules.create_get_access_code_url(
            os.environ["myob_account_authorize_url"],
            os.environ["myob_client_id"],
            os.environ["myob_redirect_uri"],
            os.environ["myob_invoice_scope"]
        )
        logging.info(f"Please visit the following URL to get the authorization code: {access_code_url}")
        #TO-DO: send an email with the URL generated above
        #Now stop this process because the log-in confirmation is done manually
        return
    else:
        # if refresh is successful, save the access_token and refresh_token to blob storage
        outputblobAccessToken.set(refreshed_result.get('access_token', ''))
        outputblobRefreshToken.set(refreshed_result.get('refresh_token', ''))
        logging.info("MYOB access token and refresh token have been updated successfully.")
        logging.info(f"New access token: {refreshed_result.get('access_token', '')}")
        logging.info(f"New refresh token: {refreshed_result.get('refresh_token', '')}")
        return refreshed_result

@app.function_name(name="func_get_new_refresh_token")
@app.route(route="func_get_new_refresh_token", methods=["GET"])
@app.blob_output(arg_name="outputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobBusinessId",
                path="teamicare/myob-authorize/business_id",
                connection="AzureWebJobsStorage")
def func_get_new_refresh_token(req: func.HttpRequest, outputblobAccessToken: func.Out[str], outputblobRefreshToken: func.Out[str], outputblobBusinessId: func.Out[str]) -> func.HttpResponse:
    # TO-DO: this function gets triggered by an HTTP GET and saves the code parameter to blob storage
    logging.info("func_get_new_refresh_token called.")
    # get the parameter 'code' and 'businessId' from the query string
    try:
        code = req.params['code']
        business_id = req.params['businessId']
    except KeyError:
        logging.error("No 'code' or 'businessId' parameter found in the request.")
        return func.HttpResponse(f"No 'code' or 'businessId' parameter found in the request.", status_code=400)
    # use the code to call the get_access_token function
    try:
        access_token_result = myob_api_modules.get_access_token(
            os.environ["myob_authorize_url"],
            os.environ["myob_client_id"],
            os.environ["myob_client_secret"],
            code,
            os.environ["myob_redirect_uri"],
            os.environ["myob_invoice_scope"]
        )
    except Exception as e:
        logging.error(f"Failed to get MYOB access token using authorization code: {e}")
        return func.HttpResponse(f"Failed to get MYOB access token using authorization code: {e}", status_code=500)
    else:
        # if successful, save the access_token and refresh_token to blob storage
        outputblobAccessToken.set(access_token_result.get('access_token', ''))
        outputblobRefreshToken.set(access_token_result.get('refresh_token', ''))
        outputblobBusinessId.set(business_id)
        logging.info("MYOB access token and refresh token have been updated successfully.")
        logging.info(f"New access token: {access_token_result.get('access_token', '')}")
        logging.info(f"New refresh token: {access_token_result.get('refresh_token', '')}")
        logging.info(f"New business ID: {business_id}")
    return access_token_result

# The following function gets MYOB company info using the access token stored in blob storage
# can be used by all actual data operation functions to check and re-authenticate if needed
# @app.blob_input(arg_name="inputblobAccessToken",
#                 path="teamicare/myob_authorize/access_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_input(arg_name="inputblobRefreshToken",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobAccessToken",
#                 path="teamicare/myob_authorize/access_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobRefreshToken",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
def func_myob_get_company_info(
        inputblobAccessToken: str, 
        inputblobRefreshToken: str, 
        outputblobAccessToken: func.Out[str], 
        outputblobRefreshToken: func.Out[str]
    ) -> dict:
    # all these operations need to call get_company_info first
    logging.info("Starting MYOB get company info process...")
    try:
        company_info_result = myob_api_modules.get_company_info(inputblobAccessToken)
    except Exception as e:
        logging.error(f"Failed to get MYOB company info: {e}, need to re-authenticate")
        # if access token is expired, refresh it
        try:
            refreshed_result = func_myob_authorize(
                inputblobRefreshToken,
                outputblobAccessToken,
                outputblobRefreshToken
            )
        except Exception as e:
            logging.error(f"Failed to refresh MYOB access token: {e}")
            return
        else:
            # if refresh is successful, retry get_company_info with new access token
            try:
                company_info_result = myob_api_modules.get_company_info(
                    refreshed_result.get('access_token', '')
                )
            except Exception as e:
                logging.error(f"Failed to get MYOB company info after refreshing access token: {e}")
                return
            else:
                logging.info(f"MYOB company info retrieved successfully after refreshing access token: {company_info_result}")
                company_info_result['_auth_info'] = refreshed_result
                return company_info_result
    else:
        logging.info(f"MYOB company info retrieved successfully: {json.dumps(company_info_result)[:100]}...")  # log only the first 100 characters
        company_info_result['_auth_info'] = {
            'access_token': inputblobAccessToken,
            'refresh_token': inputblobRefreshToken
        }
    return company_info_result

# TO-DO: build actual MYOB data functions
# always call func_myob_get_company_info above and check if return is a dict and has the 'Build' key
# if positive, proceed with actual data operations
# always use the following bindings of
# @app.blob_input(arg_name="inputblobBusinessId",
#                 path="teamicare/myob_authorize/business_id",
#                 connection="AzureWebJobsStorage")
# @app.blob_input(arg_name="inputblobAccessToken",
#                 path="teamicare/myob_authorize/access_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_input(arg_name="inputblobRefreshToken",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobAccessToken",
#                 path="teamicare/myob_authorize/access_token",
#                 connection="AzureWebJobsStorage")
# @app.blob_output(arg_name="outputblobRefreshToken",
#                 path="teamicare/myob_authorize/refresh_token",
#                 connection="AzureWebJobsStorage")
def func_myob_data_operation_example(
        inputblobBusinessId: str,
        inputblobAccessToken: str, 
        inputblobRefreshToken: str, 
        outputblobAccessToken: func.Out[str], 
        outputblobRefreshToken: func.Out[str]
    ) -> dict:
    # call func_myob_get_company_info first to ensure access token is valid
    company_info_result = func_myob_get_company_info(
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken
    )
    # if company_info_result is a dict and has the 'Build' key, proceed with actual data operations
    if isinstance(company_info_result, dict) and 'Build' in company_info_result:
        logging.info("Access token is valid, proceeding with data operations...")
        # TO-DO: add actual data operation code here
        data_operation_result = {}
        return data_operation_result
    else:
        logging.error("Access token is invalid, cannot proceed with data operations.")
        return {'error': 'Invalid access token'}

@app.function_name(name="func_filter_splose_invoice_for_myob_imports")
@app.timer_trigger(schedule="0 0 19 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_input(arg_name="inputblobBusinessId",
                path="teamicare/myob-authorize/business_id",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobSploseInvoices",
                path="teamicare/splose-outbound/splose_invoices_to_myob_import_{DateTime}.json",
                connection="AzureWebJobsStorage")
def func_filter_splose_invoice_for_myob_import(
    myTimer: func.TimerRequest,
    inputblobBusinessId: str,
    inputblobAccessToken: str, 
    inputblobRefreshToken: str, 
    outputblobAccessToken: func.Out[str], 
    outputblobRefreshToken: func.Out[str],
    outputblobSploseInvoices: func.Out[str]
):
    if myTimer.past_due:
        logging.info('The timer is past due!')
    # call func_myob_get_company_info first to ensure access token is valid
    company_info_result = func_myob_get_company_info(
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken
    )
    # if company_info_result is a dict and has the 'Build' key, proceed with actual data operations
    if isinstance(company_info_result, dict) and 'Build' in company_info_result:
        logging.info("MYOB Access token is valid, proceeding with data operations...")
    else:
        logging.error("MYOB Access token is invalid, cannot proceed with data operations.")
        return {'error': 'Invalid MYOB access token'}
    # Now proceed to filter Splose invoices for MYOB import
    splose_patient_to_contact_mapping = splose_api_modules.get_patient_to_contact_mapping()
    _ = splose_api_modules.get_all_awaiting_payment_invoices(splose_patient_to_contact_mapping)
    pending_invoice_number_list = [[str(i['id']), str(i['invoiceNumber'])] for i in _]
    # if is_local_dev is true, limit the pending_invoice_number_list to the unique list of First 20 plus last 20 items only
    if os.environ['is_local_dev'].lower() == 'true' and len(pending_invoice_number_list) > 40:
        pending_invoice_number_list = pending_invoice_number_list[:20] + pending_invoice_number_list[-20:]    
    # now check each invoice number in MYOB if it exists, if not, add to
    invoice_id_to_import_list = []
    for invoice_number in pending_invoice_number_list:
        if not myob_api_modules.is_sale_invoice_service_existing_in_myob(
            company_info_result['_auth_info'].get('access_token', ''), inputblobBusinessId, 
            splose_invoice_number=invoice_number[1]):
            invoice_id_to_import_list.append(int(invoice_number[0]))
    pending_invoices = splose_api_modules.filter_for_invoices(
        invoice_list = _,
        invoice_filter_id_list = invoice_id_to_import_list
    )
    # set the pending invoices to save into blob outputblobSploseInvoices as a pretty formatted json file for loading to another function later
    result_json_str = json.dumps(pending_invoices, ensure_ascii=False, indent=4)
    outputblobSploseInvoices.set(result_json_str)

@app.function_name(name="func_convert_splose_invoices_to_myob_customers")
@app.blob_trigger(arg_name="client",
                  source="EventGrid",
                  path="teamicare/splose-outbound",
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobBusinessId",
                path="teamicare/myob-authorize/business_id",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobMyobUpsertedCustomers",
                path="teamicare/myob-customer-outbound/myob_upserted_customers.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobMyobNewInvoices",
                path="teamicare/myob-invoice-outbound/myob_new_invoices_{DateTime}.json",
                connection="AzureWebJobsStorage")
def func_convert_splose_invoices_to_myob_customers(
    client: func.InputStream,
    inputblobBusinessId: str,
    inputblobAccessToken: str, 
    inputblobRefreshToken: str, 
    outputblobAccessToken: func.Out[str], 
    outputblobRefreshToken: func.Out[str],
    outputblobMyobUpsertedCustomers: func.Out[str],
    outputblobMyobNewInvoices: func.Out[str]
):
    # load the new file content from the blob client
    new_file_content = client.read().decode('utf-8')
    logging.info(f"New blob file content loaded: {new_file_content[:100]}...")  # log only the first 100 characters
    # call func_myob_get_company_info first to ensure access token is valid
    company_info_result = func_myob_get_company_info(
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken
    )
    # if company_info_result is a dict and has the 'Build' key, proceed with actual data operations
    if isinstance(company_info_result, dict) and 'Build' in company_info_result:
        logging.info("MYOB Access token is valid, proceeding with data operations...")
    else:
        logging.error("MYOB Access token is invalid, cannot proceed with data operations.")
        return {'error': 'Invalid MYOB access token'}
    # parse the json content to a list
    pending_invoices = json.loads(new_file_content)
    assert(
        isinstance(pending_invoices, list)
    )
    # convert the pending invoices to myob customers
    result_dict = myob_api_modules.convert_splose_invoice_to_myob_customer(
        access_token=company_info_result['_auth_info'].get('access_token', ''),
        business_id=inputblobBusinessId,
        splose_invoice_dict_list=pending_invoices
    )
    assert(
        isinstance(result_dict, dict)
    )
    # set the result dict to save into blob outputblobMyobUpsertedCustomers as a pretty formatted json file for loading to another function later
    result_json_str = json.dumps(result_dict, ensure_ascii=False, indent=4)
    outputblobMyobUpsertedCustomers.set(result_json_str)
    # set new_file_content to outputblobMyobNewInvoices for the next function to use
    outputblobMyobNewInvoices.set(new_file_content)

@app.function_name(name="func_import_splose_invoices_to_myob")
@app.blob_trigger(arg_name="client",
                  source="EventGrid",
                  path="teamicare/myob-invoice-outbound",
                  connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobBusinessId",
                path="teamicare/myob-authorize/business_id",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobMyobUpsertedCustomers",
                path="teamicare/myob-customer-outbound/myob_upserted_customers.json",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobMyobNewInvoices",
                path="teamicare/myob-invoice-inbound/myob_new_invoices_imported_{DateTime}.json",
                connection="AzureWebJobsStorage")
def func_import_splose_invoices_to_myob(
    client: func.InputStream,
    inputblobMyobUpsertedCustomers: str,
    inputblobBusinessId: str,
    inputblobAccessToken: str, 
    inputblobRefreshToken: str, 
    outputblobAccessToken: func.Out[str], 
    outputblobRefreshToken: func.Out[str],
    outputblobMyobNewInvoices: func.Out[str]
):
    # load the new file content from the blob client
    new_file_content = client.read().decode('utf-8')
    logging.info(f"New blob file content loaded: {new_file_content[:100]}...")  # log only the first 100 characters
    # call func_myob_get_company_info first to ensure access token is valid
    company_info_result = func_myob_get_company_info(
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken
    )
    # if company_info_result is a dict and has the 'Build' key, proceed with actual data operations
    if isinstance(company_info_result, dict) and 'Build' in company_info_result:
        logging.info("MYOB Access token is valid, proceeding with data operations...")
    else:
        logging.error("MYOB Access token is invalid, cannot proceed with data operations.")
        return {'error': 'Invalid MYOB access token'}
    # load the pending invoices from the blob trigger client and parse the json content to a list
    pending_invoices = json.loads(new_file_content)
    logging.info(f"Pending invoices loaded: {pending_invoices[:1]}...")  # log only the first invoice
    assert(
        isinstance(pending_invoices, list)
    )
    # load the converted customer mapping from inputblobMyobUpsertedCustomers and parse into a dict
    result_dict = json.loads(inputblobMyobUpsertedCustomers)
    assert(
        isinstance(result_dict, dict)
    )
    # now import the invoices
    imported_invoices = myob_api_modules.convert_splose_invoice_to_myob_invoice(
        access_token=company_info_result['_auth_info'].get('access_token', ''),
        business_id=inputblobBusinessId,
        splose_invoice_dict_list=pending_invoices,
        customer_uid_map=result_dict
    )
    assert(
        isinstance(imported_invoices, dict)
    )
    logging.info(f"Imported invoices result: {json.dumps(imported_invoices)[:100]}...")  # log only the first 100 characters
    # also set the imported invoices to save into blob outputblobMyobNewInvoices as a pretty formatted json file for manual inspection
    result_json_str = json.dumps(imported_invoices, ensure_ascii=False, indent=4)
    outputblobMyobNewInvoices.set(result_json_str)

@app.function_name(name="func_get_customer_payments_after_date_and_convert_to_invoice_key")
@app.timer_trigger(schedule="0 0 18 * * *", arg_name="myTimer", run_on_startup=os.environ['is_local_dev'])
@app.blob_input(arg_name="inputblobpage",
                path="teamicare/myob-payment-inbound/myob_payment_from.txt",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobBusinessId",
                path="teamicare/myob-authorize/business_id",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_input(arg_name="inputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobAccessToken",
                path="teamicare/myob-authorize/access_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobRefreshToken",
                path="teamicare/myob-authorize/refresh_token",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobMyobNewPayments",
                path="teamicare/myob-payment-outbound/myob_new_payments_{DateTime}.json",
                connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobpage",
                path="teamicare/myob-payment-inbound/myob_payment_from.txt",
                connection="AzureWebJobsStorage")
def func_get_customer_payments_after_date_and_convert_to_invoice_key(
    myTimer: func.TimerRequest,
    inputblobpage: str,
    inputblobBusinessId: str,
    inputblobAccessToken: str, 
    inputblobRefreshToken: str,
    outputblobpage: func.Out[str],
    outputblobAccessToken: func.Out[str], 
    outputblobRefreshToken: func.Out[str],
    outputblobMyobNewPayments: func.Out[str]
):
    EARLIEST_MODIFIED_DATE = '2000-01-01T00:00:00Z'
    DELTA_DAYS_FOR_NEXT_RUN = 90
    if myTimer.past_due:
        logging.info('The timer is past due!')
        # call func_myob_get_company_info first to ensure access token is valid
    company_info_result = func_myob_get_company_info(
        inputblobAccessToken,
        inputblobRefreshToken,
        outputblobAccessToken,
        outputblobRefreshToken
    )
    # if company_info_result is a dict and has the 'Build' key, proceed with actual data operations
    if isinstance(company_info_result, dict) and 'Build' in company_info_result:
        logging.info("MYOB Access token is valid, proceeding with data operations...")
    else:
        logging.error("MYOB Access token is invalid, cannot proceed with data operations.")
        return {'error': 'Invalid MYOB access token'}
    # if inputblobpage is None or empty or cannot be parsed to a date time in the format of 'YYYY-MM-DDTHH:MM:SSZ', use EARLIEST_MODIFIED_DATE
    if inputblobpage == '' or inputblobpage is None:
        blobinput = EARLIEST_MODIFIED_DATE
    else:
        try:
            blobinput = inputblobpage.strip()
            dt.strptime(blobinput, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            blobinput = EARLIEST_MODIFIED_DATE
    # now call the myob_api_modules.get_customer_payments_after_date_and_convert_to_invoice 
    after_date = dt.strptime(blobinput, '%Y-%m-%dT%H:%M:%SZ')
    resp = myob_api_modules.get_customer_payments_after_date_and_convert_to_invoice_key(
        access_token=company_info_result['_auth_info'].get('access_token', ''),
        business_id=inputblobBusinessId,
        after_date=after_date
    )
    assert(isinstance(resp, dict))
    # set the resp dict to save into blob outputblobMyobNewPayments as a pretty formatted json file for loading to another function later
    result_json_str = json.dumps(resp, ensure_ascii=False, indent=4)
    outputblobMyobNewPayments.set(result_json_str)
    # update the outputblobpage to the current date time minus 90 days
    new_after_date = dt.now() - timedelta(days=DELTA_DAYS_FOR_NEXT_RUN)
    outputblobpage.set(dt.strftime(new_after_date,'%Y-%m-%dT%H:%M:%SZ'))

@app.function_name(name="func_update_splose_invoices_with_payment_gaps")
@app.blob_trigger(arg_name="client",
                    source="EventGrid",
                    path="teamicare/myob-payment-outbound",
                    connection="AzureWebJobsStorage")
@app.blob_output(arg_name="outputblobSploseInvoicesWithPayments",
                    path="teamicare/splose-inbound/splose_invoices_updated_with_payments_{DateTime}.json",
                    connection="AzureWebJobsStorage")
def func_update_splose_invoices_with_payment_gaps(
    client: func.InputStream,
    outputblobSploseInvoicesWithPayments: func.Out[str]
):
    patient_to_contact_mapping = splose_api_modules.get_patient_to_contact_mapping()
    _ = splose_api_modules.get_all_awaiting_payment_invoices(patient_to_contact_mapping)
    # load the content from the blob client and parse into a dict
    new_file_content = client.read().decode('utf-8')
    logging.info(f"New blob file content loaded: {new_file_content[:100]}...")  # log only the first 100 characters
    payment_dict = json.loads(new_file_content)
    assert(
        isinstance(payment_dict, dict)
    )
    # Now update these invoices with payments of $1 each
    updated_invoices = splose_api_modules.update_invoices_with_payment_gaps(
        invoice_list = _,
        payment_dict = payment_dict
    )
    # set the updated invoices to save into blob outputblobSploseInvoicesWithPayments as a pretty formatted json file for manual inspection
    logging.info(f"Updated invoices: {updated_invoices[:1]}...")  #
    result_json_str = json.dumps(updated_invoices, ensure_ascii=False, indent=4)
    outputblobSploseInvoicesWithPayments.set(result_json_str)