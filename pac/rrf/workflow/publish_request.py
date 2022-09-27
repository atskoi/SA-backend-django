import json
import logging
from pac.helpers.connections import pyodbc_connection, getQueryRowResult, getQueryResults
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status, views, generics

class PublishRequest(views.APIView):
    def put(self, request, *args, **kwargs):
        request_id = request.data.get("RequestID", 0)
        publish_type = request.data.get("publishType", '')
        user_name = self.request.user.user_name
        user_id = self.request.user.user_id

        if request_id == 0:
            return Response(f"RequestID was not provided", status=status.HTTP_400_BAD_REQUEST)

        status_query = f"""SELECT RequestStatusTypeID FROM dbo.RequestStatusType WHERE RequestStatusTypeName = '{publish_type}'"""
        conn = pyodbc_connection()
        cursor = conn.cursor()
        status_id = getQueryRowResult(cursor, status_query)
        status_id = status_id.get('RequestStatusTypeID', 0)

        # validation of request tabs before publishing
        valid_counts = f"""EXEC dbo.Validate_Request @RequestID = {request_id} """
        errors = getQueryResults(cursor, valid_counts)
        errorList = []
        for error in errors:
            errorList.append(error[0])

        if len(errorList) > 0:
            return Response({"status": "failure", "errorsList": errorList }, status=status.HTTP_400_BAD_REQUEST)

        set_status = f"""
            UPDATE dbo.Request SET RequestStatusTypeID = {status_id}, CurrentEditorID = null
            WHERE RequestID = {request_id};
            EXEC dbo.[Audit_Record] @TableName = 'Request', @PrimaryKeyValue = {request_id}, @UpdatedBy = '{user_name}';
            SELECT 1 Completed;
        """

        # for queued or immediate publish requests, schedule the operation to be handled by the PricingEngine
        time_to_delay = 'DATEADD(MINUTE, 30, GETDATE())' if publish_type == 'Publish Queued' else 'GETDATE()'
        add_to_queue = f"""INSERT INTO dbo.EngineQueue
                       (OperationBody, OperationID, RequestedBy, RequestID, DueDate)
                       VALUES
                       ('{{}}', 3, {user_id}, {request_id}, {time_to_delay})"""
        cursor.execute(set_status)
        cursor.execute(add_to_queue)
        cursor.commit()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)

class ForcePublishRequest(views.APIView):

    def put(self, request, *args, **kwargs):
        request_id = request.data.get("RequestID", 0)
        publish_type = request.data.get("publishType", '')
        user_name = self.request.user.user_name
        user_id = self.request.user.user_id

        if request_id == 0:
            return Response(f"RequestID was not provided", status=status.HTTP_400_BAD_REQUEST)

        status_query = f"""SELECT RequestStatusTypeID FROM dbo.RequestStatusType WHERE RequestStatusTypeName = '{publish_type}'"""
        conn = pyodbc_connection()
        cursor = conn.cursor()
        status_id = getQueryRowResult(cursor, status_query)
        status_id = status_id.get('RequestStatusTypeID', 0)
        current_id = user_id if publish_type == 'Cancel' else 'null'

        set_status = f"""
            UPDATE dbo.Request SET RequestStatusTypeID = {status_id}, CurrentEditorID = {current_id}
            WHERE RequestID = {request_id};
            EXEC dbo.[Audit_Record] @TableName = 'Request', @PrimaryKeyValue = {request_id}, @UpdatedBy = '{user_name}';
            SELECT 1 Completed"""
        clear_queue = f"""UPDATE dbo.EngineQueue SET Completed = 1, CompletedOn = GETDATE(), Success = 0
            WHERE RequestID = {request_id}  AND Completed = 0
               AND OperationID = (SELECT OperationID FROM dbo.EngineOperation WHERE OperationName = 'Publish to TM')
            """
        cursor.execute(set_status)
        cursor.execute(clear_queue)
        cursor.commit()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)