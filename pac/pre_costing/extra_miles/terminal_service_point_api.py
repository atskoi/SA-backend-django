import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# updating rows of Terminal Service Points
class TerminalServicePointAPI(AppView):
    PRIMARY_TABLE = 'TerminalServicePoint'
    PRIMARY_KEY = 'tsp.TerminalServicePointID'
    COLUMN_MAPPING = {
        "ServicePointName": {"filterType": "textFilters", "sortColumn": 'SP.ServicePointName',
                         "filter": " AND SP.ServicePointName LIKE '%{0}%' "},
        "TerminalCode": {"filterType": "textFilters", "sortColumn": 'T.TerminalCode',
                               "filter": " AND T.TerminalCode LIKE '%{0}%' "},
        "BasingPointName": {"filterType": "textFilters", "sortColumn": 'BP.BasingPointName',
                         "filter": " AND BP.BasingPointName LIKE '%{0}%' "},
        "ProvinceCode": {"filterType": "idFilters","sortColumn": 'P.ProvinceCode', "filter": " AND P.ProvinceID IN ({0}) "},
        "UpdatedOn": {"sortColumn": "TSPH.UpdatedOn", "filter": " "}
    }

    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = '''
    {{opening_clause}}
    SELECT TSP.[TerminalServicePointID],
            T.[TerminalID],
            T.[TerminalCode] AS TerminalCode,
            SP.[ServicePointName] AS ServicePointName,
            BP.BasingPointName as BasingPointName,
            BP.Description as BasingPointLocation,
            P.[ProvinceID] AS ProvinceID,
            P.[ProvinceCode] AS ProvinceCode,
            TSP.[ExtraMiles],
            CASE WHEN TSP.IsInactiveViewable = 0 THEN 'Deleted'
                ELSE CASE WHEN TSP.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
            END AS Status,
            TSPH.[UpdatedOn]
        FROM [dbo].[TerminalServicePoint] TSP
            INNER JOIN [dbo].[ServicePoint] SP ON TSP.[ServicePointID] = SP.[ServicePointID]
            INNER JOIN [dbo].[Terminal] T ON TSP.[TerminalID] = T.[TerminalID]
            INNER JOIN dbo.V_LocationTree slt ON slt.ID = TSP.ServicePointID AND slt.PointTypeName = 'Service Point'
            INNER JOIN dbo.V_LocationTree tlt ON tlt.ID = TSP.TerminalID AND tlt.PointTypeName = 'Terminal'
            INNER JOIN dbo.BasingPoint BP ON SP.BasingPointID = BP.BasingPointID
            INNER JOIN [dbo].[Province] P on slt.ProvinceID = P.ProvinceID
            INNER JOIN [dbo].[TerminalServicePoint_History] TSPH ON TSP.[TerminalServicePointID] = TSPH.[TerminalServicePointID] AND TSPH.[IsLatestVersion] = 1
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}
    '''
    UPDATE_FIELDS = [{'fieldName': 'ExtraMiles', 'type': 'number'}]
    INSERT_FIELDS = [
        {'fieldName': 'TerminalServicePointID', 'type': 'number'},
        {'fieldName': 'TerminalID', 'type': 'number'},
        {'fieldName': 'ServicePointID', 'type': 'number'},
        {'fieldName': 'ExtraMiles', 'type': 'number'}
    ]

    SKIP_AUDIT = False

    def prepare_filter(self, data, kwargs):
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format()
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        data['records'] = update_rows
        return data