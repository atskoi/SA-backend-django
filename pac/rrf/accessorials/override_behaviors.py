import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.base_class.app_view import AppView
from pac.rrf.accessorials.base_override import BaseAccessorialOverride


class DeclaredValueOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'AccRateShippingInstructionID',
        'AccRatePercent',
        'AccRateMinCharge',
        'AccRateMaxCharge',
        'MinStdCharge']


class RangeCalculationOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'AccRateShippingInstructionID',
        'AccRateMinCharge',
        'AccRateMaxCharge',
        'MinStdCharge']


class RangePercentageOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = ['AccRateShippingInstructionID',
                     'AccRatePercent',
                     'AccRateMinCharge',
                     'AccRateMaxCharge',
                     'MinStdCharge']


class ExtraStopsOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'MinStdCharge'
    ]


class PassToClientOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'MinStdCharge'
    ]


class FlatChargeOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'AccRateShippingInstructionID',
        'MinStdCharge'
    ]


class FuelPriceOverride(BaseAccessorialOverride):
    CUSTOM_FIELDS = [
        'MinStdCharge'
    ]
