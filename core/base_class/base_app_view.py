import json
import logging
from rest_framework import views, status
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from jsonschema import validate


class BaseAppView(views.APIView):
    # if multiple actions are to be performed in a transaction, set a class-wide connection object here
    #Otherwise, the transaction is presumed to be just for this one class and will commit when it completes the operation
    conn = None
    schema = None
    user_name = None

    PRIMARY_TABLE = 'Request'
    PRIMARY_KEY = 'id'

    def fail_validation(self, data, schema):
        try:
            validate(instance=data, schema=schema)
        except Exception as e:
             # validation error returned here
             return Response({
                      'rows': [],
                      'count': 0,
                      'errorMessage': f"Body failed validation: {e}",
                      'request': data
                   }, status=status.HTTP_400_BAD_REQUEST)
        return False

    def process_sql_to_json(self, cursor, query, *args):
        cursor.execute(query)
        raw_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data_rows = []
        for row in raw_data:
            data_rows.append(dict(zip(columns, row)))
        return data_rows

    def get(self, request, *args, **kwargs):
        return Response({"status": "Success", "rows": []}, status=status.HTTP_200_OK)



    def put(self, request, *args, **kwargs):
        return Response({"status": "Success", "rowsUpdated": 0}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return Response({"status": "Success", "ids": [], "message": f"Created new records"},
        status=status.HTTP_200_OK)

    def audit_change (self, conn, primary_column, pk_id, comment):
        audit_statement = '''EXEC dbo.[Audit_Record] @TableName = '{table}', @PrimaryKeyValue = {pk_id}, @UpdatedBy = '{user_name}' '''
        audit_statement = audit_statement.format(table = self.PRIMARY_TABLE,
                                       pk_id = pk_id,
                                       user_name = self.user_name)
        # update the history table, and let any errors pass up to the error handling of calling function
        try:
            conn.execute(audit_statement)
        except Exception as e:
            logging.info(f'Failed to Audit changes on: {self.PRIMARY_TABLE} for id: {pk_id}')
