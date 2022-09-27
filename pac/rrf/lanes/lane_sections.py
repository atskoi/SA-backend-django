import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection, getQueryRowResult
from core.base_class.app_view import AppView

# updating rows of Request Sections
class LaneSection(AppView):
    PRIMARY_TABLE = 'RequestSection'
    PRIMARY_KEY = 'rs.RequestSectionID'
    GET_ALL_QUERY = """
    WITH counts AS (SELECT
        ISNULL(SUM(CASE WHEN rsl.IsActive = 1 AND rsl.[IsInactiveViewable] = 1 THEN 1 ELSE 0 END), 0) NumLanes
           	,ISNULL(SUM(CASE WHEN rsl.IsActive = 1 AND rsl.[IsInactiveViewable] = 1 AND rsl.IsPublished = 0 THEN 1 ELSE 0 END), 0) NumUnpublishedLanes
          	,ISNULL(SUM(CASE WHEN rsl.IsActive = 1 AND rsl.[IsInactiveViewable] = 1 AND rsl.IsEdited = 1 THEN 1 ELSE 0 END), 0) NumEditedLanes
          	,ISNULL(SUM(CASE WHEN rsl.IsActive = 1 AND rsl.[IsInactiveViewable] = 1 AND rsl.IsDuplicate = 1 THEN 1 ELSE 0 END), 0) NumDuplicateLanes
          	,ISNULL(SUM(CASE WHEN rsl.IsActive = 1 AND rsl.[IsInactiveViewable] = 1 AND rsl.[DoNotMeetCommitment] = 1 THEN 1 ELSE 0 END), 0) NumDoNotMeetCommitmentLanes
            , rsl.RequestSectionID
        FROM dbo.RequestSectionLane rsl
        INNER JOIN RequestSection rs ON rs.RequestSectionID = rsl.RequestSectionID
        INNER JOIN dbo.Request r ON r.RequestID = rs.RequestID
        WHERE r.RequestID = '{request_id}'
        GROUP BY rsl.RequestSectionID
    )

    SELECT rs.IsActive,rs.IsInactiveViewable,rs.RequestSectionID,rs.SectionName
        , counts.NumLanes
        , counts.NumUnpublishedLanes
        , counts.NumEditedLanes
        , counts.NumDuplicateLanes
        , counts.NumDoNotMeetCommitmentLanes
        , rs.WeightBreak
        , rs.IsDensityPricing
        , rs.OverrideDensity
        , rs.EquipmentTypeID
        , rs.OverrideClassID
        , rs.RateBaseID
        , rb.RateBaseID RateBaseGroupID
        , rb.RateBaseName RateBaseGroupName
        , rs.SubServiceLevelID
        , rs.WeightBreakHeaderID
        , rs.AsRating
        , rs.BaseRate
        , rs.HasMax
        , rs.HasMin
        , rs.UnitFactor
        , rs.CommodityID
        , rs.RequestSectionSourceID
        , ssl.SubServiceLevelCode, rb.Description, rb.RateBaseName, fc.FreightClassName, et.EquipmentTypeName
            FROM dbo.RequestSection rs
            LEFT JOIN counts ON counts.RequestSectionID = rs.RequestSectionID
            LEFT JOIN dbo.SubServiceLevel ssl ON ssl.SubServiceLevelID = rs.SubServiceLevelID
            LEFT JOIN dbo.RateBase rb ON rb.RateBaseID = rs.RateBaseID
            LEFT JOIN dbo.FreightClass fc ON fc.FreightClassID = rs.OverrideClassID
            LEFT JOIN dbo.EquipmentType et ON et.EquipmentTypeID = rs.EquipmentTypeID
            LEFT JOIN dbo.WeightBreakHeader wb ON wb.WeightBreakHeaderID = rs.WeightBreakHeaderID
            WHERE rs.RequestID = '{request_id}' {show_clause}
            ORDER BY rs.RequestSectionID"""

    UPDATE_FIELDS = [
        {'fieldName': 'SectionName', 'type': 'string'},
        {'fieldName': 'OverrideDensity', 'type': 'number'},
        {'fieldName': 'RateBaseID', 'type': 'number'},
        {'fieldName': 'CommodityID', 'type': 'number'},
        {'fieldName': 'OverrideClassID', 'type': 'number'},
        {'fieldName': 'WeightBreakHeaderID', 'type': 'number'},
        {'fieldName': 'EquipmentTypeID', 'type': 'number'},
        {'fieldName': 'WeightBreak', 'type': 'string', 'default': '[]'},
        {'fieldName': 'UnitFactor', 'type': 'number'},
        {'fieldName': 'MaximumValue', 'type': 'number'},
        {'fieldName': 'AsRating', 'type': 'boolean', 'default': False},
        {'fieldName': 'BaseRate', 'type': 'boolean', 'default': False},
        {'fieldName': 'HasMin', 'type': 'boolean', 'default': False},
        {'fieldName': 'HasMax', 'type': 'boolean', 'default': False},
    ]
    INSERT_FIELDS = [
        {'fieldName': 'SectionName', 'type': 'string'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'IsDensityPricing', 'type': 'boolean'},
        {'fieldName': 'OverrideDensity', 'type': 'number', 'default': 0},
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'RateBaseID', 'type': 'number'},
        {'fieldName': 'CommodityID', 'type': 'number'},
        {'fieldName': 'OverrideClassID', 'type': 'number'},
        {'fieldName': 'WeightBreakHeaderID', 'type': 'number'},
        {'fieldName': 'EquipmentTypeID', 'type': 'number'},
        {'fieldName': 'WeightBreak', 'type': 'string', 'default': '[]'},
        {'fieldName': 'UnitFactor', 'type': 'number'},
        {'fieldName': 'MaximumValue', 'type': 'number'},
        {'fieldName': 'AsRating', 'type': 'boolean', 'default': False},
        {'fieldName': 'BaseRate', 'type': 'boolean', 'default': False},
        {'fieldName': 'HasMin', 'type': 'boolean', 'default': False},
        {'fieldName': 'HasMax', 'type': 'boolean', 'default': False},
        {'fieldName': 'RequestSectionSourceID', 'type': 'number', 'default': 0},
    ]

    def prepare_get(self, kwargs, request):
        request_id = kwargs.get("RequestID")
        show_all = request.GET.get('showAll')
        show_clause = ' AND rs.IsInactiveViewable = 1 '
        if show_all is not None:
            show_clause = ' '
        self.GET_ALL_QUERY = self.GET_ALL_QUERY.format(
            request_id = request_id,
            show_clause = show_clause)

    def prepare_bulk_insert(self, data, kwargs):
        if not hasattr(self, 'conn') or self.conn == None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction

        cursor = self.conn.cursor()
        for row in data:
            row_data = row['data']
            wb_id = row_data['WeightBreakHeaderID']
            if wb_id is None:
                return [] # cannot complete without WB Header
            wb = getQueryRowResult(cursor,
                f'SELECT * FROM dbo.WeightBreakHeader WHERE WeightBreakHeaderID = {wb_id}')
            row_data['UnitFactor'] = wb['UnitFactor']
            row_data['MaximumValue'] = wb['MaximumValue']
            row_data['AsRating'] = wb['AsRating']
            row_data['HasMin'] = wb['HasMin']
            row_data['HasMax'] = wb['HasMax']
            row_data['BaseRate'] = wb['BaseRate']
            row_data['WeightBreak'] = wb['Levels']
            row['data'] = row_data
        return data

    def prepare_bulk_update(self, data, kwargs):
        if not hasattr(self, 'conn') or self.conn == None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        records = data['records']
        cursor = self.conn.cursor()
        for row in records:
            row_data = row['data']
            wb_id = row_data['WeightBreakHeaderID']
            if wb_id is not None: # a new WeightBreakHeader has been used (or is untouched), so refresh those values
                wb = getQueryRowResult(cursor,
                    f'SELECT * FROM dbo.WeightBreakHeader WHERE WeightBreakHeaderID = {wb_id}')
                row_data['UnitFactor'] = wb['UnitFactor']
                row_data['MaximumValue'] = wb['MaximumValue']
                row_data['AsRating'] = wb['AsRating']
                row_data['HasMin'] = wb['HasMin']
                row_data['HasMax'] = wb['HasMax']
                row_data['BaseRate'] = wb['BaseRate']
                row_data['WeightBreak'] = wb['Levels']

            row['data'] = row_data
        data['records'] = records
        return data

