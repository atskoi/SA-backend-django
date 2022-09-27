import json
import logging
from pac.helpers.connections import pyodbc_connection, getQueryRowResult, getQueryResults
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status, views, generics


class ReassignRequest(views.APIView):

    def put(self, request, *args, **kwargs):
        request_id = request.data.get("RequestID", 0)
        request_section_id = request.data.get("RequestSectionID", 0)
        new_status = request.data.get("newRequestStatus", '')
        assign_scope = request.data.get("assignScope", '')
        user_name = self.request.user.user_name

        if request_id == 0:
            return Response(f"RequestID was not provided", status=status.HTTP_400_BAD_REQUEST)
        if assign_scope == 'Section' and request_section_id == 0:
            return Response(f"RequestSectionID was not provided", status=status.HTTP_400_BAD_REQUEST)

        status_query = f"""SELECT RequestStatusTypeID FROM dbo.RequestStatusType WHERE RequestStatusTypeName = '{new_status}'"""
        conn = pyodbc_connection()
        cursor = conn.cursor()
        status_id = getQueryRowResult(cursor, status_query)
        status_id = status_id.get('RequestStatusTypeID', 0)

        # TODO: validation of request tabs before reassigning

        # determine which user should be set as current editor
        extra_setter = ''
        if new_status == 'With Pricing':
            user_query = f"""EXEC [dbo].[Get_Analyst_To_Assign] @UserType = 'Pricing Analyst', @RequestID = {request_id}; """
            new_id = getQueryRowResult(cursor, user_query)
            pricing_analyst_id = new_id.get('NextUser', 'null')
            extra_setter = f""", PricingAnalystID = {pricing_analyst_id}, CurrentEditorID = {pricing_analyst_id}"""
        if new_status == 'Sales Review':
            user_query = f"""SELECT SalesRepresentativeID, InitiatedBy FROM Request WHERE RequestID ={request_id};"""
            new_id = getQueryRowResult(cursor, user_query)
            sales_rep_id = new_id['SalesRepresentativeID']
            if sales_rep_id is None:
                sales_rep_id = new_id['InitiatedBy']
            status_type = request.data.get("StatusType", '')
            # Sales Review when approved or declined assigned with pricing
            if status_type == 'Approved':
                extra_setter = f""", SalesRepresentativeID = {sales_rep_id}, CurrentEditorID = {sales_rep_id}, ApproverID = {sales_rep_id}, SalesStatus = '{status_type}'"""
            elif status_type == 'Declined':
                extra_setter = f""", SalesRepresentativeID = {sales_rep_id}, CurrentEditorID = {sales_rep_id}, SalesStatus = '{status_type}'"""
        if new_status == 'Cost+ Analysis':
            status_type = request.data.get("StatusType", '')
            if status_type == 'Approved':
                # Cost+ when approved assigned with pricing
                user_query = f"""EXEC [dbo].[Get_Analyst_To_Assign] @UserType = 'Pricing Analyst', @RequestID = {request_id}; """
                new_id = getQueryRowResult(cursor, user_query)
                pricing_analyst_id = new_id.get('NextUser', 'null')
                status_id = 2
                extra_setter = f""", PricingAnalystID = {pricing_analyst_id}, CurrentEditorID = {pricing_analyst_id}, ApproverID = {pricing_analyst_id}, CostPlusStatus = '{status_type}'"""
            elif status_type == 'Declined':
                # Cost+ when declined assigned to sales representative
                user_query = f"""SELECT InitiatedBy FROM Request WHERE RequestID ={request_id}; """
                new_id = getQueryRowResult(cursor, user_query)
                sales_rep_id = new_id['InitiatedBy']
                status_id = 1
                extra_setter = f""", SalesRepresentativeID = {sales_rep_id}, CurrentEditorID = {sales_rep_id}, CostPlusStatus = '{status_type}'"""
        if new_status == 'With Partner Carrier':
            status_type = request.data.get("StatusType", '')
            # Partner Carrier when approved or declined assigned with pricing
            user_query = f"""EXEC [dbo].[Get_Analyst_To_Assign] @UserType = 'Pricing Analyst', @RequestID = {request_id}; """
            new_id = getQueryRowResult(cursor, user_query)
            pricing_analyst_id = new_id.get('NextUser', 'null')
            if status_type == 'Approved':
                status_id = 2
                extra_setter = f""", PricingAnalystID = {pricing_analyst_id}, CurrentEditorID = {pricing_analyst_id}, ApproverID = {pricing_analyst_id}, CarrierStatus = '{status_type}'"""
            elif status_type == 'Declined':
                status_id = 2
                extra_setter = f""", PricingAnalystID = {pricing_analyst_id}, CurrentEditorID = {pricing_analyst_id}, CarrierStatus = '{status_type}'"""
        set_status = f"""
            UPDATE dbo.Request SET RequestStatusTypeID = {status_id} {extra_setter}
            WHERE RequestID = {request_id};
            EXEC dbo.[Audit_Record] @TableName = 'Request', @PrimaryKeyValue = {request_id}, @UpdatedBy = '{user_name}';
        """
        cursor.execute(set_status)
        cursor.commit()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)
