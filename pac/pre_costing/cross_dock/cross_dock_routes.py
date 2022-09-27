import json
import logging
from rest_framework import  status, views
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView
from pac.pre_costing.line_haul_costs.lane_api import LaneAPI

# updating rows of Lane LaneRoutes
class CrossDockAPI(AppView):
    PRIMARY_TABLE = 'DockRoute'
    PRIMARY_KEY = 'dr.DockRouteID'
    COLUMN_MAPPING = {
        "OriginTerminalCode": {"filterType": "idFilters", "sortColumn": 'O.TerminalCode', "filter": " AND O.TerminalID IN ({0}) "},
        "OriginProvinceCode": {"filterType": "idFilters","sortColumn": 'O.ProvinceCode', "filter": " AND O.ProvinceID IN ({0}) "},
        "DestinationTerminalCode": {"filterType": "idFilters", "sortColumn": 'd.TerminalCode', "filter": " AND d.TerminalID IN ({0}) "},
        "DestinationProvinceCode": {"filterType": "idFilters","sortColumn": 'd.ProvinceCode', "filter": " AND d.ProvinceID IN ({0}) "},
        "SubServiceLevelCode": {"filterType": "idFilters", "sortColumn": "ssl.SubServiceLevelCode",
                                         "filter": """ AND ssl.SubServiceLevelID IN ({0}) """},
        "ServiceLevelCode": {"filterType": "idFilters", "sortColumn": "sl.ServiceLevelCode",
                                      "filter": """ AND sl.ServiceLevelID IN ({0}) """}
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = '''
    WITH T AS (
        SELECT lt.TerminalID, t.TerminalCode, lt.ProvinceID, p.ProvinceCode, lt.RegionID, r.RegionCode
        FROM dbo.V_LocationTree lt
                INNER JOIN dbo.Province p ON p.ProvinceID = lt.ProvinceID
                INNER JOIN dbo.Region r ON r.RegionID = lt.RegionID
                INNER JOIN dbo.Terminal t ON t.TerminalID = lt.ID
        WHERE lt.PointTypeName = 'Terminal'
    )
    {{opening_clause}}
    SELECT l.LaneID, dr.DockRouteID,
            dr.RouteLegs,
            dr.IsExcludeSource,
            dr.IsExcludeDestination,
            O.TerminalID AS OriginTerminalID,
            O.TerminalCode AS OriginTerminalCode,
            O.ProvinceID AS OriginProvinceID,
            O.ProvinceCode AS OriginProvinceCode,
            O.RegionID AS OriginRegionID,
            O.RegionCode AS OriginRegionCode,
            D.TerminalID AS DestinationTerminalID,
            D.TerminalCode AS DestinationTerminalCode,
            D.ProvinceID AS DestinationProvinceID,
            D.ProvinceCode AS DestinationProvinceCode,
            D.RegionID AS DestinationRegionID,
            D.RegionCode AS DestinationRegionCode,
            SSL.SubServiceLevelID,
            SSL.SubServiceLevelCode,
            sl.ServiceLevelID,
            sl.ServiceLevelCode,
            so.ServiceOfferingID,
            so.ServiceOfferingName,
            L.IsHeadhaul,
            CASE WHEN dr.IsInactiveViewable = 0 THEN 'Deleted'
                ELSE CASE WHEN dr.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
            END AS Status,
            lh.UpdatedOn
        FROM dbo.DockRoute dr
            LEFT JOIN dbo.Lane l ON l.LaneID = dr.LaneID
            INNER JOIN T AS O on O.TerminalID = L.OriginTerminalID
            INNER JOIN T AS D on D.TerminalID = L.DestinationTerminalID
            INNER JOIN dbo.SubServiceLevel SSL ON L.SubServiceLevelID = SSL.SubServiceLevelID
            INNER JOIN dbo.ServiceLevel SL ON SL.ServiceLevelID = SSL.ServiceLevelID
            INNER JOIN dbo.ServiceOffering so ON so.ServiceOfferingID = sl.ServiceOfferingID
            INNER JOIN dbo.Lane_History lh ON l.LaneID = lh.LaneID AND lh.IsLatestVersion = 1
        WHERE SL.ServiceOfferingID = {service_offering_id}
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}
    '''

    UPDATE_FIELDS = [
        {'fieldName': 'RouteLegs', 'type': 'string'},
        {'fieldName': 'IsExcludeSource', 'type': 'boolean', 'default': False },
        {'fieldName': 'IsExcludeDestination', 'type': 'boolean', 'default': False }
        ]
    INSERT_FIELDS = [
        {'fieldName': 'LaneID', 'type': 'number'},
        {'fieldName': 'RouteLegs', 'type': 'string'},
        {'fieldName': 'IsExcludeSource', 'type': 'boolean', 'default': False },
        {'fieldName': 'IsExcludeDestination', 'type': 'boolean', 'default': False }
    ]

    SKIP_AUDIT = False

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_obj = {'records': []}
        rows = data.get('records')
        if len(rows) > 0:
            conn = pyodbc_connection()
            self.conn = conn
            cursor = self.conn.cursor()
            for row in rows:
                # pack the Leg values back into a JSON string
                legs = json.dumps(row.get('RouteLegs'))
                dock_route_id = row.get('DockRouteID')
                clean_row = {}
                clean_row['id'] = dock_route_id
                clean_row['data'] = row
                clean_row['data']['RouteLegs'] = legs
                update_obj['records'].append(clean_row)
        return update_obj

    def prepare_bulk_insert(self, data, kwargs):
        # check for duplicates first
        duplicateQuery = """SELECT dr.DockRouteID, l.LaneID
                            FROM dbo.Lane l
                            LEFT JOIN dbo.DockRoute dr ON l.LaneID = dr.LaneID
                            WHERE L.DestinationTerminalID = {dId} AND L.OriginTerminalID = {oId}
                            AND L.SubServiceLevelID = {ssl} """
        if len(data) > 0:
            conn = pyodbc_connection() # get a connection and start a transaction in case multiple operations are needed
            self.conn = conn
            insert_rows = []
            for row in data:
                row_data = row.get('data')
                duplicateQuery = duplicateQuery.format(
                                    dId=row_data.get('DestinationTerminalID'),
                                    oId=row_data.get('OriginTerminalID'),
                                    ssl=row_data.get('SubServiceLevelID'))
                cursor = conn.cursor()
                cursor.execute(duplicateQuery)
                get_lane_id = cursor.fetchone()
                dock_route_id = get_lane_id[0] if get_lane_id else None
                lane_id = get_lane_id[1] if get_lane_id else None
                if lane_id is None: # add the lane if it doesn't exist
                    new_lane = LaneAPI()
                    new_lane.conn = conn
                    lane_row = {'SubServiceLevelID': row_data.get('SubServiceLevelID'), \
                        'OriginTerminalID': row_data.get('OriginTerminalID'), \
                        'DestinationTerminalID': row_data.get('DestinationTerminalID'), 'IsHeadhaul': 0 }
                    got_lane_ids = new_lane.bulk_insert([{'data': lane_row}], kwargs)
                    new_lane_id = -1
                    if got_lane_ids is not None:
                        new_lane_id = int(got_lane_ids[0])
                        row['LaneID'] = new_lane_id # add the new LaneID
                    else:
                        return None
                else:
                    row['LaneID'] =lane_id # add the existing LaneID
                x_source = row_data['IsExcludeSource'] if ('IsExcludeSource' in row_data.keys()) else False
                x_dest = row_data['IsExcludeDestination'] if ('IsExcludeDestination' in row_data.keys()) else False
                insert_rows.append({'data': {'LaneID': row['LaneID'], 'RouteLegs': json.dumps(row_data.get('RouteLegs')), \
                    'IsExcludeSource': x_source, 'IsExcludeDestination': x_dest} })
        return insert_rows