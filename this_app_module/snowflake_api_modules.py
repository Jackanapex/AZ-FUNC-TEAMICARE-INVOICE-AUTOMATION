import os
import json
from typing import List, Dict, Any
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, current_timestamp
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from snowflake.snowpark.dataframe import DataFrame as SnowparkDataFrame
from snowflake.snowpark.types import StructType

import snowflake.snowpark.exceptions as snowpark_exceptions
import logging

def flatten_dict(d, parent_key='', sep='_'):
    """
    Recursively flattens a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def _get_key_dtype_map(data_list: list[dict]) -> dict[str, type]:
    """
    Scans a list of dictionaries and returns a map of each unique key
    to the data type of its value from its first occurrence.

    Args:
        data_list: A list of dictionaries.

    Returns:
        A dictionary where keys are the unique column names and values
        are the Python data types (e.g., str, int).
    """
    schema_map = {}
    for row in data_list:
        for key, value in row.items():
            if key not in schema_map:
                # Store the type of the value only if the key is new.
                schema_map[key] = f"{type(value)}"
    return schema_map

def _serialize_nested_dicts(data_list: list[dict]) -> list[dict]:
    """
    Iterates through a list of dictionaries and converts top-level
    dictionary values into JSON strings.

    Args:
        data_list: A list of dictionaries, which may contain other
                   dictionaries as values.

    Returns:
        A new list of dictionaries with nested dicts serialized to JSON.
    """
    processed_list = []
    for row in data_list:
        new_row = {}
        for key, value in row.items():
            # Check if the value is a dictionary
            if isinstance(value, dict):
                # If it is, serialize it to a JSON string
                new_row[key] = json.dumps(value)
            else:
                # Otherwise, keep the original value
                new_row[key] = value
        processed_list.append(new_row)
    return processed_list

def get_snowflake_session(schema_name = 'snowflake_schema_raw') -> Session:
    """
    Create and return a Snowflake session using environment variables.
    
    Expected environment variables:
    - SNOWFLAKE_ACCOUNT
    - SNOWFLAKE_USER
    - SNOWFLAKE_PASSWORD
    - SNOWFLAKE_WAREHOUSE
    - SNOWFLAKE_DATABASE
    - SNOWFLAKE_SCHEMA
    """
    connection_params = {
        "account": os.getenv("snowflake_account"),
        "user": os.getenv("snowflake_user"),
        "password": os.getenv("snowflake_password"),
        "warehouse": os.getenv("snowflake_warehouse"),
        "database": os.getenv("snowflake_database"),
        "schema": os.getenv(schema_name)
    }
    
    # Check if all required parameters are provided
    missing_params = [key for key, value in connection_params.items() if not value]
    if missing_params:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_params)}")
    
    return Session.builder.configs(connection_params).create()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def insert_data_to_snowflake_table(data_to_insert: List[Dict[str, Any]], target_table: str, schema: StructType) -> Dict[str, Any]:
    """
    Insert data into an existing Snowflake table using Snowpark.
    
    Args:
        data_to_insert (List[Dict[str, Any]]): A list of JSON objects (dictionaries) to insert
        target_table (str): The name of the target Snowflake table
        
    Returns:
        Dict[str, Any]: Result information from the insert operation including:
            - rows_inserted: Number of rows successfully inserted
            - status: Success/failure status
            - message: Descriptive message about the operation
            
    Raises:
        Exception: Re-raises any Snowflake exceptions with original error information
        ValueError: If input parameters are invalid
    """
    
    # Validate inputs
    if not data_to_insert:
        raise ValueError("data_to_insert cannot be empty")
    
    if not target_table or not isinstance(target_table, str):
        raise ValueError("target_table must be a non-empty string")
    
    if not isinstance(data_to_insert, list):
        raise ValueError("data_to_insert must be a list of dictionaries")
    
    # Validate that all items in the list are dictionaries
    for i, item in enumerate(data_to_insert):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {i} is not a dictionary: {type(item)}")
    
    session = None
    try:
        # Create Snowflake session
        session = get_snowflake_session()
        
        # add additional key of "azure_insert_time" to data_to_insert
        current_timestamp_ltz = session.create_dataframe([1]).select(current_timestamp()).collect()[0]["CURRENT_TIMESTAMP()"]
        for item in data_to_insert:
            item["azure_insert_time"] = current_timestamp_ltz

        # Flatten nested dictionaries in data_to_insert
        data_to_insert = _serialize_nested_dicts(data_to_insert)

        # Create a DataFrame from the JSON data
        df = session.create_dataframe(data_to_insert, schema=schema)

        # Write the DataFrame to the target table
        # Using mode="append" to add data to existing table
        write_result = df.write.mode("append").save_as_table(target_table)
        session.sql('select 1').collect()  # Dummy query to ensure write is complete
        # now check the record count in target_table in Snowflake that with azure_insert_time value equalling current_timestamp_ltz
        rows_inserted = session.table(target_table).filter(col("azure_insert_time") == current_timestamp_ltz).count()
        
        result = {
            "rows_inserted": rows_inserted,
            "status": "success",
            "message": f"Successfully inserted {rows_inserted} rows into table {target_table}",
            "table_name": target_table
        }
        
        return result
        
    except snowpark_exceptions.SnowparkSQLException as e:
        # Re-raise Snowflake SQL exceptions with original error information
        error_msg = f"Snowflake SQL Error: {e.message} (Error Code: {e.error_code})"
        raise Exception(error_msg) from e
        
    except snowpark_exceptions.SnowparkSessionException as e:
        # Re-raise Snowflake session exceptions
        error_msg = f"Snowflake Session Error: {str(e)}"
        raise Exception(error_msg) from e
        
    except snowpark_exceptions.SnowparkDataframeException as e:
        # Re-raise Snowflake DataFrame exceptions
        error_msg = f"Snowflake DataFrame Error: {str(e)}"
        raise Exception(error_msg) from e
        
    except Exception as e:
        # Re-raise any other exceptions with context
        error_msg = f"Error inserting data into Snowflake table '{target_table}': {str(e)}"
        raise Exception(error_msg) from e
        
    finally:
        # Always close the session to free up resources
        if session:
            try:
                session.close()
            except Exception as close_error:
                # Log the close error but don't raise it as it's secondary to the main operation
                logging.warning(f"Error closing Snowflake session: {close_error}")


def insert_data_to_snowflake_table_with_schema_validation(
    data_to_insert: List[Dict[str, Any]], 
    target_table: str,
    schema: StructType
) -> Dict[str, Any]:
    """
    Insert data into an existing Snowflake table with optional schema validation.
    
    Args:
        data_to_insert (List[Dict[str, Any]]): A list of JSON objects to insert
        target_table (str): The name of the target Snowflake table
        schema (StructType): The schema of the target table
        
    Returns:
        Dict[str, Any]: Result information from the insert operation
        
    Raises:
        Exception: Re-raises any Snowflake exceptions with original error information
        ValueError: If schema validation fails or input parameters are invalid
    """
    
    # Validate inputs (reuse validation from main function)
    if not data_to_insert:
        raise ValueError("data_to_insert cannot be empty")
    
    if not target_table or not isinstance(target_table, str):
        raise ValueError("target_table must be a non-empty string")
    
    # Optional schema validation
    expected_columns = [i.replace('"', '').upper() for i in schema.names]
    if expected_columns:
        # first_row_keys in upper case
        # to match the expected_columns which are in upper case
        first_row_keys = set(key.upper() for key in data_to_insert[0].keys())
        expected_keys = set(expected_columns)
        
        missing_columns = expected_keys - first_row_keys - set(['AZURE_INSERT_TIME'])
        extra_columns = first_row_keys - expected_keys
        
        if missing_columns:
            raise ValueError(f"Missing expected columns: {list(missing_columns)}")
        
        if extra_columns:
            raise ValueError(f"Unexpected columns found: {list(extra_columns)}")
    
    # Use the main insert function
    return insert_data_to_snowflake_table(data_to_insert, target_table, schema)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def call_stored_procedure(
    sp_name: str, *args: Any
) -> dict:
    """
    Calls a stored procedure in Snowflake and returns the result.

    Args:
        sp_name: The name of the stored procedure to call (e.g., 'my_sp').
        *args: A variable number of arguments to pass to the stored procedure.

    Returns:
        The result returned by the stored procedure. The type is often a string
        or can be parsed from a Variant type if the SP returns structured data.
    """
    logging.info(f"Calling stored procedure '{sp_name}' with arguments: {args}")
    # validate inputs
    if not sp_name or not isinstance(sp_name, str):
        raise ValueError("sp_name must be a non-empty string")
    if not isinstance(args, tuple):
        raise ValueError("args must be a tuple of arguments to pass to the stored procedure")
    
    session = None
    call_output = {
        'message': 'curattion procedure not called',
        'status': 'skipped',
        'total_records_curated': 0
    }

    # The session.call method is the primary way to execute stored procedures.
    # It takes the name of the procedure followed by its arguments.
    try:
        session = get_snowflake_session(schema_name='snowflake_schema_curated')
        logging.info(f"Snowflake session created successfully.")
        result = session.call(sp_name, *args)
        logging.info(f"Successfully called stored procedure. Result: {result}")
        # put result to a call_output if it's a snowpark DataFrame
        if isinstance(result, SnowparkDataFrame):
            result = result.collect()  # Collect the DataFrame to get the results
            result_first_row = result[0] if result else None
            if result_first_row:
                call_output['message'] = result_first_row['MESSAGE'] if 'MESSAGE' in result_first_row else 'No message returned'
                call_output['status'] = result_first_row['STATUS'] if 'STATUS' in result_first_row else 'failed'
                call_output['total_records_curated'] = result_first_row['INSERTED_ROWS'] if 'INSERTED_ROWS' in result_first_row else 0
            return call_output

    except snowpark_exceptions.SnowparkSQLException as e:
        # Re-raise Snowflake SQL exceptions with original error information
        error_msg = f"Snowflake SQL Error: {e.message} (Error Code: {e.error_code})"
        raise Exception(error_msg) from e
        
    except snowpark_exceptions.SnowparkSessionException as e:
        # Re-raise Snowflake session exceptions
        error_msg = f"Snowflake Session Error: {str(e)}"
        raise Exception(error_msg) from e
        
    except snowpark_exceptions.SnowparkDataframeException as e:
        # Re-raise Snowflake DataFrame exceptions
        error_msg = f"Snowflake DataFrame Error: {str(e)}"
        raise Exception(error_msg) from e
        
    except Exception as e:
        # Re-raise any other exceptions with context
        error_msg = f"Error calling Snowflake stored procedure '{sp_name}': {str(e)}"
        raise Exception(error_msg) from e
        
    finally:
        # Always close the session to free up resources
        if session:
            try:
                session.close()
            except Exception as close_error:
                # Log the close error but don't raise it as it's secondary to the main operation
                logging.warning(f"Error closing Snowflake session: {close_error}")