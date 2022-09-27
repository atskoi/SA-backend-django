from rest_framework import generics, serializers, status, views
from rest_framework.response import Response
from core.models import Persona, User
from pac.rrf.workflow.workflow import WorkflowManager
from pac.notifications import NotificationManager
from Function_BaseRate_RateWare_Load.utils import RateWareTariffLoader
from rest_framework.permissions import AllowAny
from core.base_class.app_view import AppView
import time
import json
import logging
import requests
from pac.helpers.connections import pyodbc_connection, getQueryResults, getQueryScalarResult, getQueryRowResult
from pac.pre_costing.rateware import ltl_rate_shipment_multiple, error_code_lookup
from django.conf import settings
from azure.servicebus import ServiceBusClient, ServiceBusMessage


class PricingEngineView(views.APIView):
    def add_batch_to_queue(self, cursor, RequestID, UserID, LaneIDs, RowCount):
        current_batch = {"RequestID": RequestID, "LaneIDs": LaneIDs, "RowCount": RowCount}
        add_batch = f"""INSERT INTO dbo.EngineQueue
                       (OperationBody, OperationID, RequestedBy, RequestID)
                       VALUES
                       ('{json.dumps(current_batch)}', 1, {UserID}, {RequestID})"""
        cursor.execute(add_batch)
        cursor.execute("SELECT @@IDENTITY AS ID;")
        return cursor.fetchone()[0]

    def put(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        section_id = request.data.get('RequestSectionID')
        selected_lanes = request.data.get('RequestSectionLaneIDs')
        conn = pyodbc_connection() # get a connection
        cursor = conn.cursor()
        if section_id is not None:
            section_query = f' AND rsl.RequestSectionID = {section_id}'
        elif selected_lanes is not None and len(selected_lanes) > 0:
            sql_array =  f"( {','.join(map(str, selected_lanes))} )"
            section_query = f' AND rsl.RequestSectionLaneID IN {sql_array} '
        else:
            section_query = ' '
        get_lane_counts = f'''SELECT rsl.RequestSectionLaneID, count(pp.RequestSectionLanePricingPointID)
            FROM dbo.Request r
            INNER JOIN dbo.RequestSection rs ON rs.RequestID = r.RequestID
            INNER JOIN dbo.RequestSectionLane rsl ON rsl.RequestSectionID = rs.RequestSectionID
            LEFT JOIN dbo.RequestSectionLanePricingPoint pp ON pp.RequestSectionLaneID = rsl.RequestSectionLaneID
            WHERE r.RequestID = {request_id} {section_query}
            GROUP BY rsl.RequestSectionLaneID
            ORDER BY rsl.RequestSectionLaneID ASC'''

        lane_counts = getQueryResults(cursor, get_lane_counts)
        if lane_counts is None or len(lane_counts) == 0:
            return Response({"status": "No lanes to price"}, status=status.HTTP_200_OK)

        # get an estimated count of lanes + pricing point rows
        # if the total is < 100, run immediately and return results
        # otherwise break the set into chunks, queue up the chunks in a temp table, and notify the user of status
        BATCH_SIZE = 100
        batches = []
        batch = {"RequestID": request_id, "LaneIDs": [], "RowCount": 0}
        batches.append(batch)
        batch_index = 0
        for count in lane_counts:
            if batches[batch_index]['RowCount'] > BATCH_SIZE: # stop the current batch and start a new one
                new_batch = {"RequestID": request_id, "LaneIDs": [count[0]], "RowCount": 0}
                batches.append(new_batch)
                batch_index = batch_index + 1
            batches[batch_index]['RowCount'] = batches[batch_index]['RowCount'] + 1 # for each lane
            batches[batch_index]['RowCount'] = batches[batch_index]['RowCount'] + count[1]
            batches[batch_index]['LaneIDs'].append(count[0]) # add this lane to the set in the batch

        logging.info(f'after making batches {batches}')
        first_batch = 0
        # push other batches onto a queue
        for batch_row in batches:
            queue_id = self.add_batch_to_queue(cursor, request_id, self.request.user.user_id,
                batch_row['LaneIDs'], batch_row['RowCount'])
            # could send a REST request directly to pricing engine to trigger the first batch
            if first_batch == 0:
                first_batch = queue_id
        cursor.commit()
        return Response({"result": "Pricing request has been sent"}, status=status.HTTP_200_OK)


class WorkflowErrors(views.APIView):
    def put(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')
        section_id = request.data.get('RequestSectionID')
        selected_lanes = request.data.get('RequestSectionLaneIDs')
        conn = pyodbc_connection() # get a connection
        cursor = conn.cursor()
        if section_id is not None:
            filter_query = f' rsl.RequestSectionID = {section_id}'
        elif selected_lanes is not None and len(selected_lanes) > 0:
            sql_array =  f"( {','.join(map(str, selected_lanes))} )"
            filter_query = f' rsl.RequestSectionLaneID IN {sql_array} '
        else:
            filter_query = f' r.RequestID = {request_id}'
        clear_errors = '''UPDATE dbo.RequestSectionLane SET WorkflowErrors = '{}'
                WHERE RequestSectionLaneID IN (SELECT rsl.RequestSectionLaneID
                    FROM dbo.RequestSectionLane rsl
                    INNER JOIN dbo.RequestSection rs ON rs.RequestSectionID = rsl.RequestSectionID
                    INNER JOIN dbo.Request r ON r.RequestID = rs.RequestID
                    WHERE ''' +  filter_query + ')'

        clear_results = cursor.execute(clear_errors)
        cursor.commit()
        return Response({"result": "Workflow Errors have been cleared"}, status=status.HTTP_200_OK)

class PollPricingEngine(views.APIView):
    def get(self, request, *args, **kwargs):
        request_id = kwargs.get('request_id')

        PROXIMATE_BATCH_MINUTES = 2
        count_query = f'''
        SELECT (SELECT COUNT(1) BatchCount FROM (
          select latest.DueDate FROM EngineQueue eq
          INNER JOIN (SELECT MAX(DueDate) DueDate, RequestID FROM dbo.EngineQueue GROUP BY RequestID) latest ON latest.RequestID = eq.RequestID
          where eq.requestID = {request_id} AND eq.OperationID = 1 AND DATEDIFF(minute, eq.DueDate, latest.DueDate) <= {PROXIMATE_BATCH_MINUTES}
        ) total) TotalBatches
        ,
        (SELECT COUNT(1) BatchCount FROM (
          select latest.DueDate FROM EngineQueue eq
          INNER JOIN (SELECT MAX(DueDate) DueDate, RequestID FROM dbo.EngineQueue GROUP BY RequestID) latest ON latest.RequestID = eq.RequestID
          where eq.requestID = {request_id} AND eq.OperationID = 1 AND eq.Completed = 1 AND DATEDIFF(minute, eq.DueDate, latest.DueDate) <= {PROXIMATE_BATCH_MINUTES}
        ) total) CompletedBatches
        '''
        conn = pyodbc_connection() # get a connection
        cursor = conn.cursor()
        batch_count = getQueryRowResult(cursor, count_query)
        total = batch_count.get('TotalBatches')
        if total is None or total == 0:
            return Response({"CompletedBatches": 0, "TotalBatches": 1}, status=status.HTTP_200_OK)
        return Response(batch_count, status=status.HTTP_200_OK)