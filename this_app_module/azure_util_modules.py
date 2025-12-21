from azure.storage.blob import BlobServiceClient, StandardBlobTier
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
import logging
import os
import azure.functions as func
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception)
)
def save_content_to_blob(file_content: str, file_name: str, container_name: str) -> func.HttpResponse:
    logging.info('Starting manual blob upload via SDK...')
    try:
        # 2. Connect to Blob Storage
        # OPTION A: Using Connection String (Simpler for dev)
        if os.environ.get("is_local_dev", "false").lower() == "true":
            logging.info("Using actual connection string copied from prod environment.")
            connect_str = "DefaultEndpointsProtocol=https;AccountName=stteamicare;AccountKey=wXAReKvO0ViadYNjg7+rHHfLXkCh0ISEST7oOwiJtovMZWdKfv7UTAcHVkgI22+uWJlqSiyej04++AStrAiPGQ==;EndpointSuffix=core.windows.net"
        else:
            logging.info("Using connection string from App Setting.")
            connect_str = os.environ["AzureWebJobsStorage"]
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # OPTION B: Using Managed Identity (Best practice for your corporate environment)
        # from azure.identity import DefaultAzureCredential
        # credential = DefaultAzureCredential()
        # blob_service_client = BlobServiceClient(account_url="https://<your-storage-account>.blob.core.windows.net", credential=credential)

        # 3. Get the Blob Client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

        # 4. Upload the Blob ATOMICALLY
        # 'upload_blob' performs a single PutBlob for files < 256MB by default.
        # This prevents the "0-byte creation + write" race condition.
        blob_client.upload_blob(
            file_content,
            overwrite=True,
            blob_type="BlockBlob",
            standard_blob_tier=StandardBlobTier.Hot
        )

        logging.info(f"Successfully uploaded {file_name} in a single transaction.")
        return func.HttpResponse(f"File {file_name} uploaded successfully.", status_code=200)

    except Exception as e:
        logging.error(f"Failed to upload blob: {e}")
        return func.HttpResponse(f"Error: {e}", status_code=500)

def send_message_to_queue(message: str, queue_name: str) -> None:
    if os.environ.get("is_local_dev", "false").lower() == "true":
        logging.info("Using actual connection string copied from prod environment.")
        connect_str = "DefaultEndpointsProtocol=https;AccountName=stteamicare;AccountKey=wXAReKvO0ViadYNjg7+rHHfLXkCh0ISEST7oOwiJtovMZWdKfv7UTAcHVkgI22+uWJlqSiyej04++AStrAiPGQ==;EndpointSuffix=core.windows.net"
    else:
        logging.info("Using connection string from App Setting.")
        connect_str = os.environ["AzureWebJobsStorage"]
# 1. Instantiate the QueueClient with the Base64 encoding policy
    # The 'message_encode_policy' argument tells the client to convert 
    # your string to Base64 before sending it to Azure.
    queue_client = QueueClient.from_connection_string(
        conn_str=connect_str,
        queue_name=queue_name,
        message_encode_policy=TextBase64EncodePolicy()
    )

    try:
        # 3. Send the message
        # The SDK will convert this text to 'VGhpcyBtZXNzYWdlIHdpbGwgYmUgYXV0b21hdGljYWxseSBCYXNlNjQgZW5jb2RlZA=='
        queue_client.send_message(message)
        print(f"Successfully sent message to queue: {queue_name}")
        
    except Exception as e:
        print(f"Error sending message: {e}")