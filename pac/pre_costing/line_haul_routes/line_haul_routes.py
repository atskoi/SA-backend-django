import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView
import pac.pre_costing.queries as queries

# updating rows of LineHaul Lane Costs
class LineHaulRoutesView(AppView):
    PRIMARY_TABLE = 'LaneRoute'
    PRIMARY_KEY = 'lr.LaneRouteID'

    COLUMN_MAPPING = {
        "IsHeadHaul": {"sortColumn": "L.IsHeadhaul", "filter": " "},
        "OriginTerminalCode": {"filterType": "textFilters", "sortColumn": 'L.OriginTerminalCode', "filter": " AND L.OriginTerminalCode LIKE '%{0}%' "},
        "OriginProvinceCode": {"filterType": "idFilters","sortColumn": 'L.OriginProvinceCode', "filter": " AND L.OriginProvinceID IN ({0}) "},
        "OriginRegionCode": {"filterType": "idFilters","sortColumn": 'L.OriginRegionCode', "filter": " AND L.OriginRegionID IN ({0}) "},
        "DestinationTerminalCode": {"filterType": "textFilters", "sortColumn": 'L.DestinationTerminalCode', "filter": " AND L.DestinationTerminalCode LIKE '%{0}%' "},
        "DestinationProvinceCode": {"filterType": "idFilters","sortColumn": 'L.DestinationProvinceCode', "filter": " AND L.DestinationProvinceID IN ({0}) "},
        "DestinationRegionCode": {"filterType": "idFilters","sortColumn": 'L.DestinationRegionCode', "filter": " AND L.DestinationRegionID IN ({0}) "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'L.IsActive',
            "filter": """ AND (CASE WHEN L.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN L.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """},
        "SubServiceLevelCode": {"filterType": "idFilters", "sortColumn": "ssl.SubServiceLevelCode",
                                         "filter": """ AND ssl.SubServiceLevelID IN ({0}) """},
        "UpdatedOn": {"sortColumn": "lrh.UpdatedOn", "filter": " "}
    }

    schema = buildFilterSchema(COLUMN_MAPPING)

    SKIP_AUDIT = False

    GET_FILTERED_QUERY = """
    WITH
    L AS (
        SELECT DISTINCT l.LaneID,
            olt.TerminalID AS OriginTerminalID,
            olt.RegionID AS OriginRegionID,
            ot.Description AS OriginTerminalCode,
            org.RegionCode as OriginRegionCode,
            olt.ProvinceID as OriginProvinceID,
            op.ProvinceCode as OriginProvinceCode,
            dlt.TerminalID AS DestinationTerminalID,
            dt.Description AS DestinationTerminalCode,
            dlt.RegionID AS DestinationRegionID,
            drg.RegionCode as DestinationRegionCode,
            dlt.ProvinceID as DestinationProvinceID,
            dp.ProvinceCode as DestinationProvinceCode,
            l.SubServiceLevelID,
            l.IsHeadhaul,
            l.IsActive,
            l.IsInactiveViewable
        FROM [dbo].[Lane] l
            INNER JOIN dbo.V_LocationTree olt ON l.[OriginTerminalID] = olt.[ID] AND olt.PointTypeName = 'Terminal'
            INNER JOIN dbo.Terminal ot ON ot.TerminalID = l.OriginTerminalID
            INNER JOIN dbo.Region org ON org.RegionID = olt.RegionID
            INNER JOIN dbo.Province op ON op.ProvinceID = olt.ProvinceID
            INNER JOIN dbo.V_LocationTree dlt ON l.[DestinationTerminalID] = dlt.[ID] AND dlt.PointTypeName = 'Terminal'
            INNER JOIN dbo.Terminal dt ON dt.TerminalID = l.DestinationTerminalID
            INNER JOIN dbo.Region drg ON drg.RegionID = dlt.RegionID
            INNER JOIN dbo.Province dp ON dp.ProvinceID = dlt.ProvinceID
        WHERE l.[IsInactiveViewable] = 1
    ) 
    {{opening_clause}}
    SELECT LR.LaneRouteID as lane_route_id,
            L.OriginTerminalID,
            L.OriginTerminalCode ,
            L.OriginProvinceID,
            L.OriginProvinceCode,
            L.OriginRegionID,
            L.OriginRegionCode,
            L.DestinationTerminalID,
            L.DestinationTerminalCode,
            L.DestinationProvinceID,
            L.DestinationProvinceCode,
            L.DestinationRegionID,
            L.DestinationRegionCode,
            SSL.SubServiceLevelID,
            SSL.SubServiceLevelCode,
            L.LaneID as lane_id,
            L.IsActive,
            L.IsHeadhaul,
            LR.RouteLegs,
            LRH.UpdatedOn,
            CASE WHEN L.IsInactiveViewable = 0 THEN 'Deleted'
                ELSE CASE WHEN L.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
            END AS Status      
        FROM L
            INNER JOIN [dbo].[SubServiceLevel] SSL ON L.[SubServiceLevelID] = SSL.[SubServiceLevelID]
            INNER JOIN [dbo].[ServiceLevel] SL ON SSL.[ServiceLevelID] = SL.[ServiceLevelID] AND SL.[ServiceOfferingID]= 1
            INNER JOIN [dbo].[LaneCost] LC ON L.LaneID = LC.LaneID
            LEFT OUTER JOIN [dbo].[LaneRoute] LR ON L.[LaneID] = LR.[LaneID]
            LEFT OUTER JOIN [dbo].[LaneRoute_History] LRH ON LR.[LaneRouteID] = LRH.[LaneRouteid] AND LRH.[IsLatestVersion] = 1
        where 1=1            
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}
 """

    UPDATE_FIELDS = [
    ]

    INSERT_FIELDS = [
    ]

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id)
        return data
