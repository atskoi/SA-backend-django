import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
import pac.pre_costing.queries as queries
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView


# updating rows of SpotQuoteMargin
class SpotQuoteMarginAPI(AppView):
    PRIMARY_TABLE = 'SpotQuoteMargin'
    PRIMARY_KEY = 'sm.SpotQuoteMarginID'
    GET_ALL_QUERY = """SELECT sm.*, sl.ServiceLevelCode, op.ProvinceName OriginProvinceName, dp.ProvinceName DestinationProvinceName
                        FROM SpotQuoteMargin sm
                        INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = sm.ServiceLevelID
                        INNER JOIN dbo.Province op ON op.ProvinceID = sm.OriginProvinceID AND op.IsActive =1
                        INNER JOIN dbo.Province dp ON dp.ProvinceID = sm.DestinationProvinceID AND dp.IsActive =1
                        WHERE sm.IsActive = 1 AND sm.IsInactiveViewable = 1
                        ORDER BY sm.SpotQuoteMarginID"""
    GET_SINGLE_QUERY = """SELECT sm.*, sl.ServiceLevelCode, op.ProvinceName OriginProvinceName, dp.ProvinceName DestinationProvinceName
                          FROM SpotQuoteMargin sm
                          INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = sm.ServiceLevelID
                          INNER JOIN dbo.Province op ON op.ProvinceID = sm.OriginProvinceID AND op.IsActive =1
                          INNER JOIN dbo.Province dp ON dp.ProvinceID = sm.DestinationProvinceID AND dp.IsActive =1
                            WHERE IsActive = 1 AND IsInactiveViewable = 1
                            and sm.SpotQuoteMarginID = {spot_quote_margin_id}
                            ORDER BY sm.SpotQuoteMarginID """

    COLUMN_MAPPING = {}
    UPDATE_FIELDS = [
        {'fieldName': 'MinMargin', 'type': 'string'},
        {'fieldName': 'StdMargin', 'type': 'string'},
        {'fieldName': 'MaxMargin', 'type': 'string'},
        {'fieldName': 'UpdatedOn', 'type': 'current_datetime'}]
    INSERT_FIELDS = [
        {'fieldName': 'OriginProvinceID', 'type': 'number'},
        {'fieldName': 'DestinationProvinceID', 'type': 'number'},
        {'fieldName': 'ServiceLevelID', 'type': 'number'},
        {'fieldName': 'MinMargin', 'type': 'string'},
        {'fieldName': 'StdMargin', 'type': 'string'},
        {'fieldName': 'MaxMargin', 'type': 'string'}]

    def prepare_get(self, kwargs, request):  # function to call in preparation for running the default GET behavior
        spot_quote_margin_id = kwargs.get("SpotQuoteMarginID", None)
        if spot_quote_margin_id:
            self.GET_SINGLE_QUERY = self.GET_SINGLE_QUERY.format(spot_quote_margin_id=spot_quote_margin_id)

    def prepare_bulk_insert(self, data, kwargs):  # optional function to prepare the class or data before bulk_insert
        if not hasattr(self, 'conn'):
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        return data

    def prepare_bulk_update(self, data, kwargs):  # optional function to prepare the class or data before bulk_update
        if not hasattr(self, 'conn'):
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        return data
