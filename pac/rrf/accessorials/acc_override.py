import json
import logging
from datetime import datetime
from rest_framework.response import Response
from core.base_class.app_view import AppView
from core.schemas import buildFilterSchema

# updating rows of Accessorial Detention Override
class AccessorialDetentionOverrideAPI(AppView):
    PRIMARY_TABLE = 'AccessorialDetentionOverride'
    PRIMARY_KEY = 'ado.AccDetentionOverrideID'

    UPDATE_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'EquipmentTypeID', 'type': 'number'},  # for EquimentClass
        {'fieldName': 'ExcludeClosedDaysDetention', 'type': 'number'},
        {'fieldName': 'ExcludeClosedDaysFreeTime', 'type': 'number'},
        {'fieldName': 'FreeTimes', 'type': 'string'},
        {'fieldName': 'FreeTimeID', 'type': 'number'},  # for MaxBreak, MinBreak
        {'fieldName': 'StartBillRate', 'type': 'number'},
        {'fieldName': 'DestinationID', 'type': 'number'},
        {'fieldName': 'DestinationTypeID', 'type': 'number'},
        {'fieldName': 'OriginID', 'type': 'number'},
        {'fieldName': 'OriginTypeID', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},  # Usage Percentage
        {'fieldName': 'IsWaive', 'type': 'boolean', 'default': False},
    ]
    INSERT_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'AccHeaderID', 'type': 'number'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'BaseRate', 'type': 'boolean', 'default': False},
        {'fieldName': 'CurrencyID', 'type': 'number', 'default': 1},
        {'fieldName': 'DestinationID', 'type': 'number'},
        {'fieldName': 'DestinationTypeID', 'type': 'number'},
        {'fieldName': 'EquipmentTypeID', 'type': 'number', 'default': 1},
        {'fieldName': 'EffectiveFrom', 'type': 'string', 'default': datetime.now().strftime('%Y-%m-%d')},
        {'fieldName': 'EffectiveTo', 'type': 'string', 'default': datetime.now().strftime('%Y-%m-%d')},
        {'fieldName': 'FreeTimeID', 'type': 'number', 'default': 1},
        {'fieldName': 'IsWaive', 'type': 'boolean', 'default': False},
        {'fieldName': 'TMDetentionOverrideID', 'type': 'number', 'default': 1},
        {'fieldName': 'UseActualTime', 'type': 'boolean', 'default': False},
        {'fieldName': 'OriginTypeID', 'type': 'number', 'default' : 1},
        {'fieldName': 'OriginID', 'type': 'number'},
        {'fieldName': 'ExcludeClosedDaysDetention', 'type': 'string'},
        {'fieldName': 'ExcludeClosedDaysFreeTime', 'type': 'string'},
        {'fieldName': 'StartBillRate', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},
        {'fieldName': 'AccDetentionOverrideSourceID', 'type': 'number', 'default': 0},
        {'fieldName': 'RequestSectionID', 'type': 'number'}
    ]

# updating rows of Accessorial Storage Override
class AccessorialStorageOverrideAPI(AppView):
    PRIMARY_TABLE = 'AccessorialStorageOverride'
    PRIMARY_KEY = 'aso.AccStorageOverrideID'

    UPDATE_FIELDS = [
        {'fieldName': 'FreeDays', 'type': 'number'},
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'RateAmount', 'type': 'number'},
        {'fieldName': 'UnitID', 'type': 'number'},
        {'fieldName': 'RatePer', 'type': 'number'},
        {'fieldName': 'MinStdCharge', 'type': 'number'},
        {'fieldName': 'RateMax', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},  # Usage Percentage
        {'fieldName': 'IsWaive', 'type': 'number'},
    ]

    INSERT_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'AccHeaderID', 'type': 'number'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'BaseRate', 'type': 'boolean', 'default': False},
        {'fieldName': 'CurrencyID', 'type': 'number', 'default': 1},
        {'fieldName': 'DangerousGoods', 'type': 'boolean', 'default': False},
        {'fieldName': 'EffectiveFrom', 'type': 'string', 'default': datetime.now().strftime('%Y-%m-%d')},
        {'fieldName': 'EffectiveTo', 'type': 'string', 'default': datetime.now().strftime('%Y-%m-%d')},
        {'fieldName': 'FreeDays', 'type': 'number', 'default': 1},
        {'fieldName': 'HighValue', 'type': 'boolean', 'default': False},
        {'fieldName': 'IncludeDeliveryDay', 'type': 'boolean', 'default': False},
        {'fieldName': 'IncludeTerminalServiceCalendar', 'type': 'boolean', 'default': False},
        {'fieldName': 'IsWaive', 'type': 'boolean', 'default': False},
        {'fieldName': 'TempControlled', 'type': 'boolean', 'default': False},
        {'fieldName': 'TMStorageOverrideID', 'type': 'number', 'default': 1},
        {'fieldName': 'UnitID', 'type': 'number', 'default': 1},
        {'fieldName': 'AccStorageOverrideSourceID', 'type': 'number', 'default': 0},
        {'fieldName': 'RateAmount', 'type': 'number'},
        {'fieldName': 'RateMax', 'type': 'number'},
        {'fieldName': 'RateMin', 'type': 'number'},
        {'fieldName': 'RatePer', 'type': 'number'},
        {'fieldName': 'MinStdCharge', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},
        {'fieldName': 'RequestSectionID', 'type': 'number'}
    ]


# updating rows of Accessorial Override
class AccessorialOverrideAPI(AppView):
    PRIMARY_TABLE = 'AccessorialOverride'
    PRIMARY_KEY = 'ao.AccOverrideID'
    # allow any of the existing fields to be updated if the UI has sent it up
    # this will allow the different types of ChargeBehaviors to all be supported
    # fields that are not provided will not be altered (no defaults)
    UPDATE_FIELDS = [
        {'fieldName': 'AccRangeTypeID', 'type': 'number'},
        {'fieldName': 'AccRateCustomMaximum', 'type': 'number'},
        {'fieldName': 'AccRateCustomMinimum', 'type': 'number'},
        {'fieldName': 'AccRateMaxCharge', 'type': 'number'},
        {'fieldName': 'AccRateMinCharge', 'type': 'number'},
        {'fieldName': 'MinShipmentValue', 'type': 'number'},
        {'fieldName': 'MaxShipmentValue', 'type': 'number'},
        {'fieldName': 'MinWeightValue', 'type': 'number'},
        {'fieldName': 'MaxWeightValue', 'type': 'number'},
        {'fieldName': 'AccRateShippingInstructionID', 'type': 'number'},
        {'fieldName': 'AccRatePercent', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},
        {'fieldName': 'AccRateDock', 'type': 'boolean'},
        {'fieldName': 'AccRateExcludeLegs', 'type': 'boolean'},
        {'fieldName': 'AccRateElevator', 'type': 'boolean'},
        {'fieldName': 'AccRateFactorID', 'type': 'number'},
        {'fieldName': 'AccRateRangeTypeID', 'type': 'number'},
        {'fieldName': 'AccRateStairs', 'type': 'boolean'},
        {'fieldName': 'AccRateSurvey', 'type': 'boolean'},
        {'fieldName': 'AccRateVehicleRestricted', 'type': 'boolean'},
        {'fieldName': 'AllowBetween', 'type': 'boolean'},
        {'fieldName': 'CommodityID', 'type': 'number'},
        {'fieldName': 'IsWaive', 'type': 'boolean'}
    ]
    INSERT_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'AccHeaderID', 'type': 'number'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'CarrierMovementType', 'type': 'string', 'default': None},
        {'fieldName': 'AccRangeTypeID', 'type': 'number', 'default': 1},
        {'fieldName': 'AccRateCustomMaximum', 'type': 'number'},
        {'fieldName': 'AccRateCustomMinimum', 'type': 'number'},
        {'fieldName': 'AccRateMaxCharge', 'type': 'number'},
        {'fieldName': 'AccRateMinCharge', 'type': 'number'},
        {'fieldName': 'MinShipmentValue', 'type': 'number'},
        {'fieldName': 'MaxShipmentValue', 'type': 'number'},
        {'fieldName': 'MinWeightValue', 'type': 'number'},
        {'fieldName': 'MaxWeightValue', 'type': 'number'},
        {'fieldName': 'AccRateShippingInstructionID', 'type': 'number'},
        {'fieldName': 'AccRatePercent', 'type': 'number'},
        {'fieldName': 'UsagePercentage', 'type': 'number'},
        {'fieldName': 'AccRateDock', 'type': 'boolean', 'default': False},
        {'fieldName': 'AccRateExcludeLegs', 'type': 'boolean', 'default': False},
        {'fieldName': 'AccRateElevator', 'type': 'boolean', 'default': False},
        {'fieldName': 'AccRateFactorID', 'type': 'number'},
        {'fieldName': 'AccRateRangeTypeID', 'type': 'number'},
        {'fieldName': 'AccRateStairs', 'type': 'boolean', 'default': False},
        {'fieldName': 'AccRateSurvey', 'type': 'boolean', 'default': False},
        {'fieldName': 'AccRateVehicleRestricted', 'type': 'boolean', 'default': False},
        {'fieldName': 'AllowBetween', 'type': 'boolean', 'default': False}, #Between
        {'fieldName': 'CommodityID', 'type': 'number', 'default': 1},
        {'fieldName': 'DestinationID', 'type': 'number'},
        {'fieldName': 'OriginID', 'type': 'number'},
        {'fieldName': 'DestinationTypeID', 'type': 'number'},
        {'fieldName': 'OriginTypeID', 'type': 'number'},
        {'fieldName': 'IsWaive', 'type': 'boolean', 'default': False},
        {'fieldName': 'TMACCOverrideID', 'type': 'number', 'default': 1},
        {'fieldName': 'AccOverrideSourceID', 'type': 'number', 'default': 0},
        {'fieldName': 'RequestSectionID', 'type': 'number'}
    ]

    def prepare_bulk_update(self, data, kwargs): # optional function to prepare the class or data before bulk_update
        # TODO: based on kwargs.get('ChargeBehaviorCode'), switch out the primary table and primary key for AccDention or AccStorage tables
        return data

    def prepare_bulk_insert(self, data, kwargs): # optional function to prepare the class or data before bulk_insert
        # TODO: based on kwargs.get('ChargeBehaviorCode'), switch out the primary table and primary key for AccDention or AccStorage tables
        return data