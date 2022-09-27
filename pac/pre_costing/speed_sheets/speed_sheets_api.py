import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
import pac.pre_costing.queries as queries
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# updating rows of Speed Sheets
class SpeedSheetAPI(AppView):
    PRIMARY_TABLE = 'SpeedSheet'
    PRIMARY_KEY = 'ss.SpeedSheetID'
    COLUMN_MAPPING = {
        "SpeedSheetID": {"filterType": "textFilters", "sortColumn": 'ss.SpeedSheetID',
                               "filter": " AND ss.SpeedSheetID LIKE '%{0}%' "},
        "Margin": {"filterType": "textFilters", "sortColumn": 'ss.Margin',
                               "filter": " AND ss.Margin LIKE '%{0}%' "},
        "MaxDensity": {"filterType": "textFilters", "sortColumn": 'ss.MaxDensity',
                   "filter": " AND ss.MaxDensity LIKE '%{0}%' "},
        "MinDensity": {"filterType": "textFilters", "sortColumn": 'ss.MinDensity',
                   "filter": " AND ss.MinDensity LIKE '%{0}%' "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'ss.IsActive',
                     "filter": """ AND (CASE WHEN tc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN ss.IsActive = 0 THEN 2 ELSE 1 END
                    END) IN ({0}) """},
        "UpdatedOn": {"sortColumn": "tch.UpdatedOn", "filter": " "}
    }

    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = queries.SPEED_SHEET_REDUCED_DASHBOARD
    UPDATE_FIELDS = [{'fieldName': 'Margin', 'type': 'number'},
                    {'fieldName': 'MaxDensity', 'type': 'number'},
                    {'fieldName': 'MinDensity', 'type': 'number'}]
    INSERT_FIELDS = [
        {'fieldName': 'SpeedSheetID', 'type': 'number'},
        {'fieldName': 'Margin', 'type': 'number'},
        {'fieldName': 'MaxDensity', 'type': 'number'},
        {'fieldName': 'MinDensity', 'type': 'number'}
    ]

    SKIP_AUDIT = False

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        data['records'] = update_rows
        return data