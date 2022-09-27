import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
import pac.pre_costing.queries as queries
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# updating rows of Terminal Costs
class TerminalCostAPI(AppView):
    PRIMARY_TABLE = 'TerminalCost'
    PRIMARY_KEY = 'tc.TerminalCostID'
    COLUMN_MAPPING = {
        "TerminalCode": {"filterType": "textFilters", "sortColumn": 'T.TerminalCode',
                               "filter": " AND T.TerminalCode LIKE '%{0}%' "},
        "CityName": {"filterType": "textFilters", "sortColumn": 'C.CityName',
                               "filter": " AND C.CityName LIKE '%{0}%' "},
        "ProvinceCode": {"filterType": "idFilters","sortColumn": 'P.ProvinceCode', "filter": " AND P.ProvinceID IN ({0}) "},
        "RegionName": {"filterType": "textFilters", "sortColumn": 'R.RegionName',
                                           "filter": " AND R.RegionName LIKE '%{0}%' "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'tc.IsActive',
                     "filter": """ AND (CASE WHEN tc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN tc.IsActive = 0 THEN 2 ELSE 1 END
                    END) IN ({0}) """},
        "UpdatedOn": {"sortColumn": "tch.UpdatedOn", "filter": " "}
    }

    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = queries.TERMINAL_COSTS_REDUCED_DASHBOARD
    UPDATE_FIELDS = [{'fieldName': 'Cost', 'type': 'string'},
                     {'fieldName': 'IsIntraRegionMovementEnabled', 'type': 'number'},
                     {'fieldName': 'IntraRegionMovementFactor', 'type': 'number'}]
    INSERT_FIELDS = [
        {'fieldName': 'TerminalID', 'type': 'number'},
        {'fieldName': 'IsIntraRegionMovementEnabled', 'type': 'number'},
        {'fieldName': 'IntraRegionMovementFactor', 'type': 'number'}
    ]

    SKIP_AUDIT = False

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        if len(update_rows) > 0:
            for row in update_rows:
                # pack the cost values back into the DB expected JSON formatting
                values = row.get('data')
                costs = {"CostComponents" : { "CostByWeightBreak" : {}, "CrossDockCost" : {}}}
                intraRegionEnabled = False
                regionEnabled = 0
                regionFactor = 1
                for fieldName in values:
                    if fieldName == 'CrossDockCostPerWeightUnit' or fieldName == 'CrossDockCostMin' or fieldName == 'CrossDockCostMax' :
                        costs["CostComponents"]["CrossDockCost"][fieldName] = float(values.get(fieldName))
                    elif fieldName == 'IntraRegionMovementFactor':
                        intraRegionEnabled = True
                        regionFactor = values.get(fieldName)
                    elif fieldName == 'IsIntraRegionMovementEnabled':
                        regionEnabled = values.get(fieldName)
                    else :
                        costs["CostComponents"]["CostByWeightBreak"][fieldName] = float(values.get(fieldName))

                if intraRegionEnabled:
                    row['data'] = {'Cost': json.dumps(costs), 'IsIntraRegionMovementEnabled' : int(regionEnabled), 'IntraRegionMovementFactor' : regionFactor}
                else :
                    row['data'] = {'Cost': json.dumps(costs)}
        data['records'] = update_rows
        return data