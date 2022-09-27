import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.base_class.app_view import AppView
from core.schemas import buildFilterSchema

class BaseAccessorialOverride(AppView):
    PRIMARY_KEY = 'AccDetailID'
    GET_FILTERED_QUERY = """{{opening_clause}}
        SELECT * FROM (
        SELECT
            ad.AccDetailID,
            null AccOverrideID,
            null RequestID,
            null RequestSectionID,
            null RequestSectionName,
            ad.SubServiceLevelID,
            ssl.SubServiceLevelName,
            ssl.SubServiceLevelCode,
            'Standard' RowType,
            ad.AllowBetween,
            null UsagePercentage,
            null IsWaive,
            ad.OriginTypeID, lto.PointTypeName OriginType, ad.OriginID, lto.Code OriginCode, lto.Name OriginName,
            ad.DestinationTypeID, ltd.PointTypeName DestinationType, ad.DestinationID, ltd.Code DestinationCode, ltd.Name DestinationName,
            {base_columns}
        FROM AccessorialDetail ad
        INNER JOIN SubServiceLevel ssl on ad.SubServiceLevelID = ssl.SubServiceLevelID
        INNER JOIN ServiceLevel sl on ssl.ServiceLevelID = sl.ServiceLevelID
        INNER JOIN dbo.V_LocationTree lto ON lto.PointTypeID = ad.OriginTypeID AND lto.ID = ad.OriginID
        INNER JOIN dbo.V_LocationTree ltd ON ltd.PointTypeID = ad.DestinationTypeID AND ltd.ID = ad.DestinationID
        WHERE ad.AccHeaderID = {acc_header_id} AND NOT EXISTS (SELECT * FROM dbo.AccessorialOverride ao
            WHERE ao.AccHeaderID = ad.AccHeaderID
            AND ao.OriginTypeID = ad.OriginTypeID
            AND ao.OriginID = ad.OriginID
            AND ao.DestinationTypeID = ad.DestinationTypeID
            AND ao.DestinationID = ad.DestinationID
            AND ao.SubServiceLevelID = ad.SubServiceLevelID
            AND ao.RequestID = {request_id}
            )
        UNION ALL
        SELECT
            ad.AccDetailID,
            ao.AccOverrideID,
            ao.RequestID,
            ao.RequestSectionID,
            rs.SectionName RequestSectionName,
            ao.SubServiceLevelID,
            ssl.SubServiceLevelName,
            ssl.SubServiceLevelCode,
            CASE 
              WHEN ad.AccDetailID IS NULL AND ao.OriginTypeID IS NULL AND ao.OriginID IS NULL AND ao.DestinationTypeID IS NULL AND ao.DestinationID IS NULL AND ao.RequestSectionID IS NULL THEN 'Header' 
              WHEN ad.AccDetailID IS NULL THEN 'Override'
              ELSE 'Merged' END RowType,
            ao.AllowBetween,
            ao.UsagePercentage,
            ao.IsWaive,
            ao.OriginTypeID, lto.PointTypeName OriginType, ao.OriginID, lto.Code OriginCode, lto.Name OriginName,
            ao.DestinationTypeID, ltd.PointTypeName DestinationType, ao.DestinationID, ltd.Code DestinationCode, ltd.Name DestinationName,
            {override_columns}
        FROM AccessorialOverride ao
        LEFT JOIN dbo.AccessorialDetail ad ON ao.AccHeaderID = ad.AccHeaderID
            AND ao.OriginTypeID = ad.OriginTypeID
            AND ao.OriginID = ad.OriginID
            AND ao.DestinationTypeID = ad.DestinationTypeID
            AND ao.DestinationID = ad.DestinationID
            AND ao.SubServiceLevelID = ad.SubServiceLevelID
        left join SubServiceLevel ssl on ao.SubServiceLevelID = ssl.SubServiceLevelID
        left join ServiceLevel sl on ssl.ServiceLevelID = sl.ServiceLevelID
        LEFT JOIN dbo.RequestSection rs ON rs.RequestSectionID = ao.RequestSectionID
        left JOIN dbo.V_LocationTree lto ON lto.PointTypeID = ao.OriginTypeID AND lto.ID = ao.OriginID
        left JOIN dbo.V_LocationTree ltd ON ltd.PointTypeID = ao.DestinationTypeID AND ltd.ID = ao.DestinationID
        WHERE ao.AccHeaderID = {acc_header_id} AND ao.RequestID = {request_id}
        ) src
      {{where_clauses}} {{sort_clause}} {{page_clause}} {{closing_clause}} """
    COLUMN_MAPPING = {
        "OriginCode": {"filterType": "textFilters","sortColumn": 'OriginCode', "filter": " AND OriginCode LIKE '%{0}%' "},
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    UPDATE_FIELDS = []
    INSERT_FIELDS = []

    def prepare_filter(self, data, kwargs): # optional function to prepare the class or data before filtering
        acc_header_id = kwargs.get("AccHeaderID")
        request_id = kwargs.get("RequestID")
        # build out the OG and current value column definitions
        base_strs = []
        ov_strs = []
        for field in self.CUSTOM_FIELDS:
            base_strs.append(f'ad.{field} OG{field}, ad.{field}')
            ov_strs.append(f'ad.{field} OG{field}, COALESCE(ao.{field}, ad.{field}) {field}')

        base_columns = ','.join(base_strs)
        override_columns =  ','.join(ov_strs)

        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(
            request_id=request_id,
            acc_header_id=acc_header_id,
            base_columns=base_columns,
            override_columns=override_columns
            )
        return data
