import json
import logging
from rest_framework import generics, mixins, status, views
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection, getQueryScalarResult
import pac.pre_costing.queries as queries
from pac.pre_costing.line_haul_costs.lane_api import LaneAPI
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView
from pac.rrf.models import RequestSection, PointType
from pac.rrf.service_matrix_validation import validate_new_lane




class RequestSectionLaneHelper(object):

    def __init__(self,conn):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.point_types = {
                        1: 'Country', 2: 'Region', 3: 'Province', 4: 'Terminal',
                        5: 'BasingPoint', 6: 'ServicePoint', 7: 'PostalCode'}

    def endpoint_exists(self, group_id, point_id):
        cursor = self.cursor
        valid_query = '''
            SELECT CASE WHEN v.found = 0 THEN 'false' ELSE 'true' END valid
            FROM (
                SELECT count(*) as found
                WHERE ({group_id} = 1 AND EXISTS (SELECT * FROM dbo.Country WHERE CountryID = {point_id}))
                OR ({group_id} = 2 AND EXISTS (SELECT * FROM dbo.Region WHERE RegionID = {point_id}))
                OR ({group_id} = 3 AND EXISTS (SELECT * FROM dbo.Province WHERE ProvinceID = {point_id}))
                OR ({group_id} = 4 AND EXISTS (SELECT * FROM dbo.Terminal WHERE TerminalID = {point_id}))
                OR ({group_id} = 5 AND EXISTS (SELECT * FROM dbo.BasingPoint WHERE BasingPointID = {point_id}))
                OR ({group_id} = 5 AND EXISTS (SELECT * FROM dbo.Zone WHERE ZoneID = {point_id}))
                OR ({group_id} = 6 AND EXISTS (SELECT * FROM dbo.ServicePoint WHERE ServicePointID = {point_id}))
                OR ({group_id} = 7 AND EXISTS (SELECT * FROM dbo.PostalCode WHERE PostalCodeID = {point_id}))
            ) as v'''
        valid_query = valid_query.format(
            group_id=group_id,
            point_id=point_id)
        cursor.execute(valid_query)
        is_valid = cursor.fetchone()
        is_valid = is_valid[0] if is_valid else 1 # will trigger an error for this lane
        if is_valid == 'false':
            return f"Lane endpoint does not exist: ID: {point_id} "
        else:
            return None


    def get_bulk_points(self, point_type_id, point_group_type_id, point_group_value_id,
        service_type_id, sub_service_level_id):
        conn = self.conn
        group_type_field_name = "{point_type_name}ID".format(
            point_type_name=self.point_types.get(point_group_type_id))
        points_query = """
            SELECT DISTINCT lt.PointTypeID, lt.ID as PointID
            FROM dbo.V_LocationTree lt
            LEFT JOIN dbo.ServiceMatrix sm ON sm.PointTypeID = 4 and sm.PointID = lt.TerminalID  AND sm.SubServiceLevelID = {sub_service_level_id}
            WHERE lt.PointTypeID = {point_type_id}
            AND lt.{group_type_field_name} = {point_group_value_id}
            AND sm.ServiceTypeID = {service_type_id}
            """.format(point_type_id=point_type_id,
               group_type_field_name=group_type_field_name,
               point_group_value_id=point_group_value_id,
               sub_service_level_id=sub_service_level_id,
               service_type_id=service_type_id)

        cursor = self.cursor
        cursor.execute(points_query)
        columns = [column[0] for column in cursor.description]
        points = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return points

    def get_filtered_lanes(self, data):
        conn = self.conn
        bulk_lanes = []
        for rec in data:
            destination_service_type_id = rec.get('DestinationServiceTypeID', None)
            origin_service_type_id = rec.get('OriginServiceTypeID', None)

            #only trigger bulk lanes creation when service type is set in origin or destination
            if not (origin_service_type_id or destination_service_type_id):
                bulk_lanes.append(rec)
                continue

            destination_bulk_filter_type = rec.get('DestinationBulkFilterPointType', None)
            destination_id = rec.get('DestinationID', None)
            destination_group_type_id = rec.get('DestinationGroupType', None)
            destination_group_value_id = rec.get('DestinationGroupValue', None)
            destination_type_id = rec.get('DestinationTypeID', None)
            origin_bulk_filter_type = rec.get('OriginBulkFilterPointType', None)
            origin_id = rec.get('OriginID', None)
            origin_group_type_id = rec.get('OriginGroupType', None)
            origin_group_value_id = rec.get('OriginGroupValue', None)
            origin_type_id = rec.get('OriginTypeID', None)
            is_between = rec['IsBetween']
            request_section_id = rec['RequestSectionID']
            sub_service_level_id = RequestSection.objects.get(pk=request_section_id).sub_service_level.sub_service_level_id

            if origin_service_type_id:
                # origin_group_type_id = origin_bulk_filter_type
                origin_points = self.get_bulk_points(origin_bulk_filter_type, origin_group_type_id,
                                                          origin_group_value_id, origin_service_type_id, sub_service_level_id )
            else:
                origin_points = [{'PointTypeID': origin_group_type_id, 'PointID': origin_group_value_id}]

            if destination_service_type_id:
                destination_points = self.get_bulk_points(destination_bulk_filter_type, destination_group_type_id,
                                                               destination_group_value_id, destination_service_type_id, sub_service_level_id)
            else:
                destination_points = [{'PointTypeID': destination_group_type_id,
                                      'PointID': destination_group_value_id}]

            bulk_lanes += [
                {'RequestSectionID': request_section_id, 'IsBetween': is_between,
                 'OriginTypeID': orp['PointTypeID'], 'OriginID': orp['PointID'],
                 'DestinationTypeID': dsp['PointTypeID'], 'DestinationID': dsp['PointID']
                 }
                for orp in origin_points
                for dsp in destination_points
            ]

        return bulk_lanes


class RequestLaneValidator(views.APIView):
    def put(self, request, *args, **kwargs):
        lanes = []
        initial_lanes = request.data.get('lanes')

        if initial_lanes is None:
            return Response({"status": "Failure", "message": f"No Lanes included"},
                    status=status.HTTP_400_BAD_REQUEST)
        lane_errors = []
        conn = pyodbc_connection() # get a connection and start a transaction in case multiple operations are needed
        cursor = conn.cursor()
        for lane in initial_lanes:
            origin_filter = lane.get('OriginServiceTypeID')
            dest_filter = lane.get('DestinationServiceTypeID')
            if origin_filter is None and dest_filter is None:
                # verify that the single lane is valid in the service matrix (because we are not selecting a serviceTypeID)
                origin_id = lane.get('OriginID')
                origin_type_id = lane.get('OriginTypeID')
                dest_id = lane.get('DestinationID')
                dest_type_id = lane.get('DestinationTypeID')
                request_section_id = lane.get('RequestSectionID')
                sub_service_level_id = RequestSection.objects.get(pk=request_section_id).sub_service_level.sub_service_level_id
                check_serviceable = '''
                SELECT COUNT(*) FROM (
                SELECT DISTINCT lt.PointTypeID, lt.ID as PointID, st.ServiceTypeName
                    FROM dbo.V_LocationTree lt
                    LEFT JOIN dbo.ServiceMatrix sm ON sm.PointTypeID = 4 and sm.PointID = lt.TerminalID  AND sm.SubServiceLevelID = {ssl}
                    LEFT JOIN dbo.ServiceType st ON st.ServiceTypeID = sm.ServiceTypeID
                    WHERE (lt.PointTypeID = {origin_type_id} AND lt.ID = {origin_id}) OR (lt.PointTypeID = {dest_type_id} AND lt.ID = {dest_id})
                ) src WHERE src.ServiceTypeName IN ('EMBARGO', 'NOSERVICE')
                '''.format(ssl=sub_service_level_id,
                    origin_type_id=origin_type_id,
                    origin_id=origin_id,
                    dest_type_id=dest_type_id,
                    dest_id=dest_id)
#                 cursor.execute(check_serviceable)
                count_invalid = getQueryScalarResult(cursor, check_serviceable)
                if count_invalid > 0:
                    return Response({"status": "Failure", "message": f"Lanes include an unserviceable location"},
                                        status=status.HTTP_400_BAD_REQUEST)

        # lanes are valid so far, so spread into a set of lanes if there is a serviceType filter
        rslh = RequestSectionLaneHelper(conn)
        lanes = rslh.get_filtered_lanes(request.data.get('lanes'))

        # if the total count of lanes now exceeds the configured maximum, reject the validation of the request
        number_of_lanes = len(lanes)
        LANE_LIMIT = 20000 #TODO retrieve from configured value
        if number_of_lanes > LANE_LIMIT:
            lane_errors.append(
                f": Failure attempting to add {number_of_lanes}, lanes which exceeds the {LANE_LIMIT} lane limit")
            return Response({"status": "Failure", "errors": lane_errors, "message": f"Lane count exceeds limit"},
                        status=status.HTTP_400_BAD_REQUEST)
        if number_of_lanes < 1:
            lane_errors.append( f": No Valid lanes could be added")
            return Response({"status": "Failure", "errors": lane_errors, "message": f"No valid lanes"},
                status=status.HTTP_400_BAD_REQUEST)
        dupe_ids_to_check = []
        section_id=lanes[0].get('RequestSectionID')
        for lane in lanes:
            is_between = 1 if lane.get('IsBetween') == True else 0
            insert_val = f"({lane.get('OriginTypeID')},{lane.get('OriginID')},{lane.get('DestinationTypeID')}, {lane.get('DestinationID')}, {is_between})"
            dupe_ids_to_check.append(insert_val)

        dupe_ids_to_check = ','.join(dupe_ids_to_check)

        duplicate_query = '''
        SET NOCOUNT ON
        DECLARE @dupeTable as Table(
            OriginTypeID INT,
            OriginID BIGINT,
            DestinationTypeID INT,
            DestinationID BIGINT,
            IsBetween BIT
        )
        INSERT INTO @dupeTable VALUES {dupe_ids_to_check};

        SELECT count(*) FROM (
        SELECT
        dt.OriginTypeId,
        dt.OriginID,
        dt.DestinationTypeID,
        dt.DestinationID,
        dt.IsBetween,
        COUNT(rsl.RequestSectionLaneID) DuplicateCount
        FROM @dupeTable dt
        LEFT JOIN dbo.RequestSectionLane rsl ON rsl.RequestSectionID = {section_id}
            AND ((rsl.OriginTypeID = dt.OriginTypeID AND rsl.OriginID = dt.OriginID AND rsl.DestinationTypeID = dt.DestinationTypeID AND rsl.DestinationID = dt.DestinationID)
                OR ((rsl.IsBetween = 1 OR dt.IsBetween = 1)
                AND rsl.OriginTypeID = dt.DestinationTypeID AND rsl.OriginID = dt.DestinationID AND rsl.DestinationTypeID = dt.OriginTypeID AND rsl.DestinationID = dt.OriginID)
                )
        GROUP BY dt.OriginTypeId,dt.OriginID,dt.DestinationTypeID,dt.DestinationID,dt.IsBetween) src
        WHERE src.DuplicateCount > 0;
        '''

        # verify that no lanes will not be a duplicate
        duplicate_query = duplicate_query.format(
            dupe_ids_to_check=dupe_ids_to_check,
            section_id=section_id)
#         cursor.execute(duplicate_query)
        count_dupes = getQueryScalarResult(cursor, duplicate_query)
        if count_dupes > 0:
            lane_errors.append(f"Duplicate lane detected: Section:{section_id} Total duplicates: {count_dupes} ")

        # if any lanes had error, return the problems
        if len(lane_errors) == 0:
            return Response({"status": "Success", "type": "validation", "message": f"Lanes are valid"},
                status=status.HTTP_200_OK)
        else:
            return Response({"status": "Failure", "errors": lane_errors, "message": f"Not all lanes are valid"},
                        status=status.HTTP_400_BAD_REQUEST)

# operations on Lanes within a Section of a Request
class RequestSectionLaneView(AppView):
    PRIMARY_TABLE = 'RequestSectionLane'
    PRIMARY_KEY = 'rsl.RequestSectionLaneID'

    INSERT_FIELDS = [
        {'fieldName': 'RequestSectionID', 'type': 'number'},
        {'fieldName': 'OriginTypeID', 'type': 'number'},
        {'fieldName': 'OriginID', 'type': 'number'},
        {'fieldName': 'DestinationTypeID', 'type': 'number'},
        {'fieldName': 'DestinationID', 'type': 'number'},
        {'fieldName': 'IsBetween', 'type': 'boolean', 'default': 0},
        {'fieldName': 'RequestSectionLaneSourceID', 'type': 'number', 'default': 'null'},
        {'fieldName': 'Deficit', 'type': 'string', 'default': None},
        {'fieldName': 'EmbeddedCost', 'type': 'string', 'default': None},
        {'fieldName': 'ImpactPercentage', 'type': 'string', 'default': None}

    ]
    INSERT_PROCEDURE = '''EXEC [dbo].[RequestSectionLane_Insert] {}, {}, null, {}, {}, null, {}, {}, 0, null, {}, {}, {}, {}'''
    # INSERT_PROCEDURE_FIELDS = ['RequestSectionID','OriginTypeID', 'OriginID', 'DestinationTypeID','DestinationID', 'IsBetween', 'RequestSectionLaneSourceID']
    # a new pattern where the stored procedure in place is too complex to attempt to model in python
    # instead, the required fields to run the procedure are pulled in and applied
    # the new auditing pattern is applied after the proc runs

    UPDATE_FIELDS = [
        {'fieldName': 'EmbeddedCost', 'type': 'string'},
        {'fieldName': 'Cost', 'type': 'string'},
    ]
    GET_FILTERED_QUERY = """{{opening_clause}}
        SELECT
            rsl.IsActive, rsl.IsInactiveViewable
            ,rsl.RequestSectionLaneID, rsl.RequestSectionID
            ,rsl.IsPublished,rsl.IsEdited,rsl.IsDuplicate,rsl.IsBetween
            ,dlt.ID DestinationID
            ,dlt.PointTypeID DestinationTypeID
            ,dlt.Name DestinationName
            ,dlt.PointTypeName DestinationType
            ,olt.ID OriginID
            ,olt.PointTypeID OriginTypeID
            ,olt.Name OriginName
            ,olt.PointTypeName OriginType
            ,Cost
            ,DoNotMeetCommitment ,Commitment,CustomerRate,CustomerDiscount,DrRate,PartnerRate,PartnerDiscount
            ,Profitability ,PickupCount,DeliveryCount,DockAdjustment,Margin,Density,PickupCost,DeliveryCost
            ,PricingRates,WorkflowErrors,IsExcluded,IsFlagged
            ,Deficit, EmbeddedCost, ImpactPercentage
            ,rsl.RequestSectionLaneSourceID
            ,CASE WHEN rsl.IsDuplicate = 1 THEN 'Duplicated'
                 WHEN rsl.IsEdited = 1 THEN 'Edited' 
                 WHEN rsl.IsBetween = 1 THEN 'Between'
                 WHEN rsl.Cost = (SELECT JSON_QUERY((SELECT NULL as Cost FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS Uncosted) THEN 'Uncosted'
                ELSE CASE WHEN rsl.WorkflowErrors != 'NULL' THEN 'Error' ELSE 'New' END
            END AS Status
        FROM dbo.RequestSectionLane rsl
        INNER JOIN dbo.V_LocationTree olt ON olt.ID = rsl.OriginID AND olt.PointTypeID = rsl.OriginTypeID
        INNER JOIN dbo.V_LocationTree dlt ON dlt.ID = rsl.DestinationID AND dlt.PointTypeID = rsl.DestinationTypeID
        INNER JOIN dbo.RequestSection rs ON rs.RequestSectionID = rsl.RequestSectionID
        WHERE {section_clause} AND rsl.IsActive = 1 AND rs.IsActive = 1
        {{where_clauses}} 
        {{sort_clause}} 
        {{page_clause}} 
        {{closing_clause}} """
    COLUMN_MAPPING = {
        "OriginID": {"filterType": "idFilters", "sortColumn": 'rsl.OriginID', "filter": " AND rsl.OriginID IN ({0}) "},
        "OriginName": {"filterType": "textFilters", "sortColumn": 'olt.Name', "filter": " AND olt.Name LIKE '{0}%' "},
        "LaneStatusID": {"filterType": "idFilters", "sortColumn": '',
                         "filter": """ AND (CASE  WHEN rsl.Cost = (SELECT JSON_QUERY((SELECT NULL as Cost FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)) AS Uncosted) THEN 6 WHEN rsl.IsBetween = 1 THEN 5 
                                    WHEN rsl.WorkflowErrors != 'NULL' THEN 4 WHEN rsl.IsDuplicate = 1 THEN 3 
                                    ELSE CASE WHEN rsl.IsEdited = 1 THEN 2 ELSE 1 END
                    END) IN ({0}) """}}

    schema = buildFilterSchema(COLUMN_MAPPING)

    def prepare_filter(self, data, kwargs):
        section_id = kwargs.get('RequestSectionID')
        section_clause = f' rsl.RequestSectionID = {section_id}'
        if section_id is None:
            request_id = kwargs.get('RequestID')
            section_clause = f' rs.RequestID = {request_id}'
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(section_clause=section_clause)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        if len(update_rows) > 0:
            for row in update_rows:
                values = row.get('data')
                costs = json.dumps(values)
                target = row.get('targetColumn')
                # only the two cost columns for now
                target = 'Cost' if target == 'costData' else 'Commitment'
                row['data'] = {}
                row['data'][target] = costs
        data['records'] = update_rows
        return data

    def prepare_bulk_insert(self, data, kwargs):
        conn = self.conn if self.conn else pyodbc_connection()
        rslh = RequestSectionLaneHelper(conn)
        lane_data = [row.get('data') for row in data]
        bulk_lanes = [ dict(data=l) for l in rslh.get_filtered_lanes(lane_data)]
        return bulk_lanes
