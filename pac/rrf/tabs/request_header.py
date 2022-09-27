
import json
import logging
logging.getLogger().setLevel(logging.INFO)
from pac.helpers.connections import pyodbc_connection
import pac.rrf.queries as queries
from rest_framework.response import Response
from rest_framework import status, views

class RequestHeader(views.APIView):
    # gets counts related to a specific request for the header above the request
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.user_id
        request_id = kwargs.get("RequestID")
        version_num = kwargs.get("version_num")
        query = queries.GET_REQUEST_HEADER.format(request_id, user_id)
        if version_num is not None: # get the requested version instead
            query = queries.GET_REQUEST_HEADER_HISTORY.format(request_id, version_num, user_id)

        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)
