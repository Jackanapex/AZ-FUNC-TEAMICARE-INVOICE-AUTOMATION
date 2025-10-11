# from simple_salesforce import Salesforce, SalesforceLogin

# SOQL_MAX_COLUMNS = 200

# class SalesforceApi:
#     def __init__(self, username=None, password=None, security_token=None, session_id=None, instance=None, sandbox=False):
#         self.username = username
#         self.password = password
#         self.security_token = security_token
#         self.sandbox = sandbox
#         self.session_id = session_id
#         self.instance = instance
#         self.sf = None
    
#     def renew_session(self):
#         if self.sandbox:
#             self.session_id, self.instance = SalesforceLogin(username=self.username, password=self.password, security_token=self.security_token, domain='test')
#         else:
#             self.session_id, self.instance = SalesforceLogin(username=self.username, password=self.password, security_token=self.security_token)
#         return self.session_id, self.instance
    
#     def connect(self):
#         if self.session_id and self.instance:
#             self.sf = Salesforce(instance=self.instance, session_id=self.session_id)

#     def get_objects(self, query_columns: list = [], object_name: str = None, query_filter: str = None):
#         """
#         Get a list of objects from Salesforce.

#         :param object_name: The name of the object to query.
#         :param query_columns: A list of columns to query.
#         :param query_filter: A filter to apply to the query.
#         """
#         query_columns = ['FIELDS(ALL)'] if len(query_columns) == 0 else query_columns[:SOQL_MAX_COLUMNS]
#         query_columns_str = ', '.join(query_columns)
#         if query_filter:
#             result = self.sf.query_all(f"SELECT {query_columns_str} FROM {object_name} WHERE {query_filter}")
#         else:
#             result = self.sf.query_all(f"SELECT {query_columns_str} FROM {object_name}")
#         return result
