# """
# Demonstrates how to authenticate with user credentials (username and password) in non-interactive mode


# """

# from office365.sharepoint.client_context import ClientContext
# from office365.sharepoint.files.system_object_type import FileSystemObjectType
# from datetime import datetime as dt
# import logging

# def _authenticate_web_sharepoint_session(site_url: str, username: str, password: str):
#     try:
#         ctx = ClientContext(site_url).with_client_credentials(username, password)
#         web = ctx.web.get().execute_query()
#         if web.url:
#             logging.info(f"Successfully authenticated to {web.url}")
#             return ctx
#     except Exception as e:
#         logging.info(f"Failed to authenticate: {e}")
#         return None

# def _get_web_all_items(ctx, folder_server_relative_url=None, modified_since=None, file_type='.csv'):
#     output_items = []
#     # Parse modified_since from string to datetime
#     modified_since = dt.strptime(modified_since, "%Y-%m-%d %H:%M:%S") if modified_since else dt(2024, 1, 1, 0, 0, 0)
#     if folder_server_relative_url:
#         doc_lib = ctx.web.default_document_library()
#         items = (
#             doc_lib.items.select(["FileSystemObjectType"])
#             .expand(["File", "Folder"])
#             .get_all()
#             .execute_query()
#         )
#         for idx, item in enumerate(items):
#             if item.file_system_object_type == FileSystemObjectType.File and \
#                 item.file.serverRelativeUrl.startswith(folder_server_relative_url) and \
#                 item.file.name.endswith(file_type) and \
#                 item.file.time_last_modified >= modified_since:
#                 file = {
#                     "file": item.file.serverRelativeUrl,
#                     "name": item.file.name,
#                     "last_modified": item.file.time_last_modified
#                 }
#                 logging.info(f"File found: {file}")
#                 output_items.append(file)
#     return output_items

# def _download_file(ctx, file_server_relative_url):
#     try:
#         file_content = (
#             ctx.web.get_file_by_server_relative_path(file_server_relative_url)
#             .get_content()
#             .execute_query()
#         )
#         logging.info(f"File downloaded: {file_server_relative_url}")
#         return file_content.value.decode("latin1")
#     except Exception as e:
#         logging.info(f"Failed to download file: {e}")
#         return '-1'
