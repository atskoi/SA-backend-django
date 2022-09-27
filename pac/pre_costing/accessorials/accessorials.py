from enum import IntEnum
from datetime import datetime
import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# class definition for the AccessorialHeader that contains the TMCode and ChargeBehavior definitions
class AccessorialHeaderAPI(AppView):
    PRIMARY_TABLE = 'AccessorialHeader'
    PRIMARY_KEY = 'ah.AccHeaderID'
    GET_ALL_QUERY = """SELECT acb.AccChargeBehavior, acb.TMChargeBehaviorCode, ah.* FROM AccessorialHeader ah 
                        left JOIN dbo.AccChargeBehavior acb  
                        ON ah.AccChargeBehaviorID = acb.AccChargeBehaviorID
                        WHERE ah.IsActive = 1 AND ah.IsInactiveViewable = 1
                        AND acb.IsActive = 1 AND acb.IsInactiveViewable = 1
                        ORDER BY ah.AccHeaderID"""
    GET_SINGLE_QUERY = """SELECT * FROM AccessorialHeader ah 
                            WHERE IsActive = 1 AND IsInactiveViewable = 1
                            and ah.AccHeaderID = {acc_header_id}                            
                            ORDER BY ah.AccHeaderID"""


# main class to retrieve all Business Standard Accessorial values
class AccessorialDetailsAPI(AppView):
    PRIMARY_TABLE = 'AccessorialDetail'
    PRIMARY_KEY = 'ad.AccDetailID'
    # GET Queries
    GET_FILTERED_QUERY = """{{opening_clause}}
        SELECT ad.AccHeaderID,
            ad.OriginTypeID, lto.PointTypeName OriginType, ad.OriginID, lto.Code OriginCode, lto.Name OriginName,
            ad.DestinationTypeID, ltd.PointTypeName DestinationType, ad.DestinationID, ltd.Code DestinationCode, ltd.Name DestinationName,
            ssl.SubServiceLevelID, ssl.SubServiceLevelCode, ssl.SubServiceLevelName, sl.ServiceLevelID, sl.ServiceLevelName,
            {charge_code_columns}
        inner join dbo.SubServiceLevel ssl on ad.SubServiceLevelID = ssl.SubServiceLevelID
        inner join dbo.ServiceLevel sl on ssl.ServiceLevelID = sl.ServiceLevelID
        INNER JOIN dbo.V_LocationTree lto ON lto.PointTypeID = ad.OriginTypeID AND lto.ID = ad.OriginID
        INNER JOIN dbo.V_LocationTree ltd ON ltd.PointTypeID = ad.DestinationTypeID AND ltd.ID = ad.DestinationID
        WHERE ad.AccHeaderID = {header_id}
        {{where_clauses}} {{sort_clause}} {{page_clause}} {{closing_clause}}
    """
    QUERIES_BY_CHARGE_CODE = {
        'DV': """
            ad.AccDetailID,
            ad.AllowBetween,
            ad.AccRateShippingInstructionID,
            ad.AccRateRangeField1ID,
            ad.AccRatePercent,
            ad.AccRateMinCharge,
            ad.AccRateMaxCharge,
            ad.AccRateFactorID,
            ad.MinStdCharge
            FROM dbo.AccessorialDetail ad """,
        'FL': """
            ad.AccDetailID,
            ad.AllowBetween,
            ad.AccRateShippingInstructionID,
            ad.AccRateFactorID,
            ad.MinStdCharge
            FROM dbo.AccessorialDetail ad """,
        'FP': """
            ad.AccDetailID,
            ad.AccRateFuelPriceAverage FuelProgram,
            ad.MinStdCharge
            FROM dbo.AccessorialDetail ad """,
        'RC': """
            ad.AccDetailID,
            ad.AllowBetween,
            ad.AccRateShippingInstructionID,
            ad.AccRateRangeField1ID,
            ad.AccRateMinCharge,
            ad.AccRateMaxCharge,
            ad.AccRateFactorID,
            ad.MinStdCharge
            FROM dbo.AccessorialDetail ad""",
        'RP': """
            ad.AccDetailID,
            ad.AllowBetween,
            ad.AccRateShippingInstructionID,
            ad.AccRateRangeField1ID,
            ad.AccRatePercent,
            ad.AccRateMinCharge,
            ad.AccRateMaxCharge,
            ad.MinStdCharge
            FROM dbo.AccessorialDetail ad""",

        'DETPPU': """
            ad.AccDetentionID,
            et.EquipmentTypeName EquipmentClass,
            ad.ExcludeClosedDaysDetention,
            ad.ExcludeClosedDaysFreeTime,
            ad.FreeTimeUnit,
            ad.freetimes,
            ad.freetimeunitofmeasure WBUOM,
            ft.MinBreak,
            ft.MaxBreak,
            ad.StartBillRate
            from dbo.AccessorialDetention ad
            inner join dbo.EquipmentType et on ad.EquipmentTypeID = et.EquipmentTypeID
            inner join dbo.FreeTime ft on ad.FreeTimeID = ft.free_time_id """,
        'DETPDL': """
            ad.AccDetentionID,
            et.EquipmentTypeName EquipmentClass,
            ad.ExcludeClosedDaysDetention,
            ad.ExcludeClosedDaysFreeTime,
            ad.FreeTimeUnit,
            ad.freetimes,
            ad.StartBillRate
            from AccessorialDetention ad
            inner join EquipmentType et on ad.EquipmentTypeID = et.EquipmentTypeID """,
        'STORAG': """
                 ad.AccStorageID,
                 ad.FreeDays,
                 ad.RateAmount,
                 un.UnitName,
                 ad.RatePer,
                 ad.MinStdCharge,
                 ad.RateMax
               from dbo.AccessorialStorage ad
               inner join unit un on acs.unitID = un.unitID"""
    }
    COLUMN_MAPPING = {
        "OriginCode": {"filterType": "textFilters","sortColumn": 'lto.Code', "filter": " AND lto.Code LIKE '%{0}%' "},
    }
    schema = buildFilterSchema(COLUMN_MAPPING)

    def prepare_filter(self, data, kwargs):
        charge_behavior_code = kwargs.get("TMChargeBehaviorCode")
        acc_header_id = kwargs.get("AccHeaderID")

        behavior_query = ' from dbo.AccessorialDetail ad '
        if charge_behavior_code in self.QUERIES_BY_CHARGE_CODE:
            behavior_query = self.QUERIES_BY_CHARGE_CODE[charge_behavior_code]
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(charge_code_columns=behavior_query, header_id=acc_header_id)
        return data
