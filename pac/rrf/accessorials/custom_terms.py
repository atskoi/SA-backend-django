import io
import html
import json
import logging
logging.getLogger().setLevel(logging.INFO)
import pyodbc
from rest_framework import status, views
from rest_framework.response import Response
from jsonschema import validate
from pac.helpers.connections import pyodbc_connection
from pac.email.send_email import send_email_simple
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# updating rows of Terms
class TermsAPI(AppView):
    PRIMARY_TABLE = 'Terms'
    PRIMARY_KEY = 'te.AccTermID'
    GET_ALL_QUERY = """SELECT * FROM Terms te
                        WHERE te.IsActive = 1 AND te.IsInactiveViewable = 1
                        AND te.RequestID = {request_id}
                        ORDER BY te.AccTermID
                    """
    GET_SINGLE_QUERY = """SELECT * FROM Terms te
                            WHERE IsActive = 1 AND IsInactiveViewable = 1
                            and te.AccTermID = {acc_term_id}
                            ORDER BY te.AccTermID"""

    COLUMN_MAPPING = {
     }
    schema = buildFilterSchema(COLUMN_MAPPING)
    UPDATE_FIELDS = [
        {'fieldName': 'CustomTerms', 'type': 'string'},
        {'fieldName': 'Status', 'type': 'number'},
        {'fieldName': 'IsActive', 'type': 'number'},
        {'fieldName': 'IsInactiveViewable', 'type': 'number'},
    ]
    INSERT_FIELDS = [
        {'fieldName': 'CustomTerms', 'type': 'string'},
        {'fieldName': 'Status', 'type': 'number'},
        {'fieldName': 'RequestID', 'type': 'number'},
    ]

    def prepare_bulk_insert(self, data, kwargs):
        if not hasattr(self, 'conn'):
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        for row in data: #zero out all statuses
            row["Status"] = 0
        return data

    def prepare_bulk_update(self, data, kwargs): # optional function to prepare the class or data before bulk_update
        if not hasattr(self, 'conn'):
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        return data

    def prepare_get(self, kwargs, request): # function to call in preparation for running the default GET behavior
        acc_term_id = kwargs.get("AccTermID", None)
        request_id = kwargs.get("RequestID")
        if acc_term_id:
            self.GET_SINGLE_QUERY = self.GET_SINGLE_QUERY.format(acc_term_id = acc_term_id)
        else:
            self.GET_ALL_QUERY = self.GET_ALL_QUERY.format(request_id = request_id)

# handler for email specific users of changes to the Request Accessorials CustomTerms
class CustomTermsEmail(views.APIView):
    CustomTermsEmailSchema = {
        "type": "object",
        "properties": {
                        "cc": {
                            "type": "array",
                            "items": {"type": "string", "format":"email"}
                        },
                        "body" : {"type" : "string"},
                        "subject" : {"type" : "string"},
                        "to" : {"type" : "string", "format":"email"},
        },
        "required": ["to"]
    }

    def post(self, request, *args, **kwargs):

        try:
            #get the custom terms for this request
            data = request.data
            request_id = kwargs.get('request_id')
            custom_terms_query = """
                select ct.AccTermID, ct.CustomTerms, ct.Status, r.RequestID from dbo.Request r
                inner join dbo.Terms ct on r.RequestID = ct.RequestID
                where r.RequestID={request_id} and r.IsActive = 1 and ct.IsActive = 1 and ct.Status = 0;            
            """

            # get connection.
            conn = pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute(
                custom_terms_query.format(request_id=request_id))
            columns = [column[0] for column in cursor.description]
            terms_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            term_ids = []
            # Send Email
            if terms_data:
                # validate request body
                validate(instance=data, schema=self.CustomTermsEmailSchema)

                #prepare the email elements
                custom_terms = "\n\n".join([row['CustomTerms'] for row in terms_data])
                body = 'The following Custom Terms Have been created or updated :\n\n' + custom_terms
                cc = data.get('cc', [])
                subject = data.get('subject', 'Created Or Updated Custom Terms')
                to = [data.get('to')]

                #send the email
                send_email_simple(subject=subject, body=html.unescape(body), to=to, cc=cc)

                #update the statuses of terms emailed
                terms_api = TermsAPI()
                terms_api.conn = conn
                post_data = [dict(id=row['AccTermID'], data= dict(Status=1)) for row in terms_data]
                term_ids = terms_api.update_records(dict(records = post_data), args, kwargs)
                conn.commit()
            return Response({
                "request": data,
                "term_ids" : term_ids,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            conn.rollback()
            return Response({
                'errorMessage': "The email request is missing required information",
                'request': data
            }, status=status.HTTP_400_BAD_REQUEST)