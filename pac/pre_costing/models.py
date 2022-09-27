from django.db import models
from django.dispatch import receiver
from datetime import datetime

from core.models import User
from pac.helpers.base import CommentUpdateDelete, Delete
from pac.models import (Province, ProvinceHistory, ServiceLevel,
                        ServiceLevelHistory, ServiceMode, ServiceModeHistory,
                        ServiceOffering, ServiceOfferingHistory, ServicePoint,
                        ServicePointHistory, Terminal, TerminalHistory, Unit,
                        UnitHistory, BasingPoint, BasingPointHistory, SubServiceLevel, SubServiceLevelHistory)
from pac.rrf.models import (FreightClass)


class RequestLog(models.Model):
    RATEWARE = "RateWare"
    SYSTEM_CHOICES = [(RATEWARE, "RateWare")]

    reference_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ReferenceId")
    request = models.TextField(null=False, blank=False, db_column="Request")
    response = models.TextField(null=False, blank=False, db_column="Response")
    timestamp = models.DateTimeField(
        auto_now_add=True, null=False, db_column="Timestamp")
    system = models.CharField(
        max_length=99, null=False, blank=False, db_column="System")
    is_succesful = models.BooleanField(
        null=False, default=True, db_column="IsSuccesful")
    error_log = models.TextField(blank=True, null=True, db_column="ErrorLog")

    def __str__(self):
        return str(self.reference_id)

    class Meta:
        verbose_name_plural = 'RequestLog'
        db_table = 'RequestLog'


class TerminalCost(Delete):
    terminal_cost_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalCostID")
    terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="TerminalID")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    is_intra_region_movement_enabled = models.BooleanField(
        default=False, null=False, db_column="IsIntraRegionMovementEnabled")
    intra_region_movement_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="IntraRegionMovementFactor")
    cost = models.TextField(
        default="[]", null=False, blank=False, db_column="Cost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.terminal_cost_id)

    class Meta:
        index_together = (("terminal", "service_offering"))
        verbose_name_plural = 'TerminalCost'
        db_table = 'TerminalCost'


class TerminalCostHistory(CommentUpdateDelete):
    terminal_cost_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalCostVersionID")
    terminal_cost = models.ForeignKey(
        TerminalCost, on_delete=models.CASCADE, db_column="TerminalCostID")
    terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, db_column="TerminalVersionID")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    is_intra_region_movement_enabled = models.BooleanField(
        default=False, null=False, db_column="IsIntraRegionMovementEnabled")
    intra_region_movement_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="IntraRegionMovementFactor")
    cost = models.TextField(
        default="[]", null=False, blank=False, db_column="Cost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.terminal_cost_version_id)

    class Meta:
        index_together = (("terminal_cost", "version_num"))
        verbose_name_plural = 'TerminalCost_History'
        db_table = 'TerminalCost_History'

class UnitConversion(Delete):
    unit_conversion_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UnitConversionID")
    from_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, db_column="FromUnitID", related_name="+")
    to_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, db_column="ToUnitID", related_name="+")
    conversion_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="ConversionFactor")

    def __str__(self):
        return str(self.unit_conversion_id)

    class Meta:
        index_together = (('from_unit', 'to_unit'))
        verbose_name_plural = 'UnitConversion'
        db_table = 'UnitConversion'


class UnitConversionHistory(CommentUpdateDelete):
    unit_conversion_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UnitConversionVersionID")
    unit_conversion = models.ForeignKey(
        UnitConversion, on_delete=models.CASCADE, db_column="UnitConversionID")
    from_unit_version = models.ForeignKey(
        UnitHistory, on_delete=models.CASCADE, db_column="FromUnitVersionID", related_name="+")
    to_unit_version = models.ForeignKey(
        UnitHistory, on_delete=models.CASCADE, db_column="ToUnitVersionID", related_name="+")
    conversion_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="ConversionFactor")

    def __str__(self):
        return str(self.unit_conversion_version_id)

    class Meta:
        index_together = (('unit_conversion', 'version_num'))
        verbose_name_plural = 'UnitConversion_History'
        db_table = 'UnitConversion_History'


class Lane(Delete):
    lane_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LaneID")
    origin_terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="OriginTerminalID", related_name="+")
    destination_terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="DestinationTerminalID", related_name="+")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelID")
    is_headhaul = models.BooleanField(
        null=False, default=True, db_column="IsHeadhaul")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.lane_id)

    class Meta:
        index_together = (
            ('origin_terminal', 'destination_terminal'))
        verbose_name_plural = 'Lane'
        db_table = 'Lane'


class LaneHistory(CommentUpdateDelete):
    lane_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LaneVersionID")
    lane = models.ForeignKey(
        Lane, on_delete=models.CASCADE, db_column="LaneID")
    origin_terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, db_column="OriginTerminalVersionID", related_name="+")
    destination_terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, db_column="DestinationTerminalVersionID", related_name="+")
    sub_service_level_version = models.ForeignKey(
        SubServiceLevelHistory, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelVersionID")
    is_headhaul = models.BooleanField(
        null=False, default=True, db_column="IsHeadhaul")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.lane_version_id)

    class Meta:
        index_together = (('lane', 'version_num'))
        verbose_name_plural = 'Lane_History'
        db_table = 'Lane_History'


@receiver(models.signals.post_save, sender=Lane)
def post_save_lane(sender, instance, created, **kwargs):
    create_lane_history(instance)


def create_lane_history(instance):
    history_instance = LaneHistory()
    previous_history_instance = LaneHistory.objects.filter(
        lane=instance, is_latest_version=True).first()

    history_instance.lane = instance

    for field in ["origin_terminal", "destination_terminal"]:
        field_history_instance = TerminalHistory.objects.filter(
            terminal=getattr(instance, field), is_latest_version=True).first()
        if field_history_instance:
            setattr(history_instance, field +
                    "_version", field_history_instance)

    for field in ["service_level"]:
        field_history_instance = ServiceLevelHistory.objects.filter(
            service_level=getattr(instance, field), is_latest_version=True).first()
        if field_history_instance:
            setattr(history_instance, field +
                    "_version", field_history_instance)

    for field in ["is_headhaul", "is_active", "is_inactive_viewable"]:
        setattr(history_instance, field, getattr(instance, field))

    if previous_history_instance:
        history_instance.version_num = previous_history_instance.version_num + 1
        previous_history_instance.is_latest_version = False
        previous_history_instance.save()

    history_instance.save()


class LaneRoute(Delete):
    lane_route_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LaneRouteID")
    lane = models.ForeignKey(
        Lane, on_delete=models.CASCADE, db_column="LaneID")
    route_legs = models.TextField(
        null=False, blank=False, default="[]", db_column="RouteLegs")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.lane_route_id)

    class Meta:
        verbose_name_plural = 'LaneRoute'
        db_table = 'LaneRoute'


class LaneRouteHistory(CommentUpdateDelete):
    lane_route_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LaneRouteVersionID")
    lane_route = models.ForeignKey(
        LaneRoute, on_delete=models.CASCADE, db_column="LaneRouteID")
    lane_version = models.ForeignKey(
        LaneHistory, on_delete=models.CASCADE, db_column="LaneVersionID")
    route_legs = models.TextField(
        null=False, blank=False, default="[]", db_column="RouteLegs")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.lane_route_version_id)

    class Meta:
        index_together = (('lane_route', 'version_num'))
        verbose_name_plural = 'LaneRoute_History'
        db_table = 'LaneRoute_History'


class DockRoute(Delete):
    is_exclude_source = models.BooleanField(
        null=False, default=False, db_column="IsExcludeSource")
    is_exclude_destination = models.BooleanField(
        null=False, default=False, db_column="IsExcludeDestination")
    dock_route_id = models.BigAutoField(
        primary_key=True, null=False, db_column="DockRouteID")
    lane = models.ForeignKey(
        Lane, on_delete=models.CASCADE, db_column="LaneID")
    route_legs = models.TextField(
        null=False, blank=False, default="[]", db_column="RouteLegs")

    def __str__(self):
        return str(self.dock_route_id)

    class Meta:
        verbose_name_plural = 'DockRoute'
        db_table = 'DockRoute'


class DockRouteHistory(CommentUpdateDelete):
    dock_route_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="DockRouteVersionID")
    dock_route = models.ForeignKey(
        DockRoute, on_delete=models.CASCADE, db_column="DockRouteID")
    lane_version = models.ForeignKey(
        LaneHistory, on_delete=models.CASCADE, db_column="LaneVersionID")
    route_legs = models.TextField(
        null=False, blank=False, default="[]", db_column="RouteLegs")
    is_exclude_source = models.BooleanField(
        null=False, default=False, db_column="IsExcludeSource")
    is_exclude_destination = models.BooleanField(
        null=False, default=False, db_column="IsExcludeDestination")

    def __str__(self):
        return str(self.dock_route_version_id)

    class Meta:
        index_together = (('dock_route', 'version_num'))
        verbose_name_plural = 'DockRoute_History'
        db_table = 'DockRoute_History'


class LaneCost(Delete):
    lane_cost_id = models.BigAutoField(primary_key=True, null=False, db_column="LaneCostID")
    lane = models.ForeignKey(Lane, on_delete=models.CASCADE, db_column="LaneID")
    cost = models.TextField(null=False, blank=False, default="{}", db_column="Cost")
    minimum_cost = models.DecimalField(max_digits=19, decimal_places=6, null=False, db_column="MinimumCost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    # maximum_cost = models.DecimalField(max_digits=19, decimal_places=6, null=False, db_column="MaximumCost")

    def __str__(self):
        return str(self.lane_cost_id)

    class Meta:
        verbose_name_plural = 'LaneCost'
        db_table = 'LaneCost'


class LaneCostHistory(CommentUpdateDelete):
    lane_cost_version_id = models.BigAutoField(primary_key=True, null=False, db_column="LaneCostVersionID")
    lane_cost = models.ForeignKey(LaneCost, on_delete=models.CASCADE, db_column="LaneCostID")
    lane_version = models.ForeignKey(LaneHistory, on_delete=models.CASCADE, db_column="LaneVersionID")
    cost = models.TextField(null=False, blank=False, default="{}", db_column="Cost")
    minimum_cost = models.DecimalField(max_digits=19, decimal_places=6, null=False, db_column="MinimumCost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    # maximum_cost = models.DecimalField(max_digits=19, decimal_places=6, null=False, db_column="MaximumCost")

    def __str__(self):
        return str(self.lane_cost_version_id)

    class Meta:
        index_together = (('lane_cost', 'version_num'))
        verbose_name_plural = 'LaneCost_History'
        db_table = 'LaneCost_History'


class LegCost(Delete):
    leg_cost_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LegCostID")
    lane = models.ForeignKey(
        Lane, on_delete=models.CASCADE, db_column="LaneID")
    service_mode = models.ForeignKey(
        ServiceMode, on_delete=models.CASCADE, db_column="ServiceModeID")
    cost = models.TextField(
        null=False, blank=False, default="{}", db_column="Cost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.leg_cost_id)

    class Meta:
        index_together = (('lane', 'service_mode'))
        verbose_name_plural = 'LegCost'
        db_table = "LegCost"


class LegCostHistory(CommentUpdateDelete):
    leg_cost_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LegCostVersionID")
    leg_cost = models.ForeignKey(
        LegCost, on_delete=models.CASCADE, db_column="LegCostID")
    lane_version = models.ForeignKey(
        LaneHistory, on_delete=models.CASCADE, db_column="LaneVersionID")
    service_mode_version = models.ForeignKey(
        ServiceModeHistory, on_delete=models.CASCADE, db_column="ServiceModeVersionID")
    cost = models.TextField(
        null=False, blank=False, default="{}", db_column="Cost")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.leg_cost_version_id)

    class Meta:
        index_together = (('leg_cost', 'version_num'))
        verbose_name_plural = 'LegCost_History'
        db_table = "LegCost_History"


class BrokerContractCost(Delete):
    broker_contract_cost_id = models.BigAutoField(
        primary_key=True, null=False, db_column="BrokerContractCostID")
    terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="TerminalID")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelID")
    cost_by_weight_break = models.TextField(
        null=False, blank=False, default="{}", db_column="Cost")
    pickup_delivery_count = models.IntegerField(
        null=True, blank=True, default=0, db_column="PickupDeliveryCount")
    rate_base = models.DecimalField(
        null=True, blank=True, decimal_places=6, max_digits=19, db_column="RateBase")
    rate_max = models.DecimalField(
        null=True, blank=True, decimal_places=6, max_digits=19, db_column="RateMax")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.broker_contract_cost_id)

    class Meta:
        verbose_name_plural = 'BrokerContractCost'
        db_table = "BrokerContractCost"


class BrokerContractCostHistory(CommentUpdateDelete):
    broker_contract_cost_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="BrokerContractCostVersionID")
    broker_contract_cost = models.ForeignKey(
        BrokerContractCost, on_delete=models.CASCADE, db_column="BrokerContractCostID")
    terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, db_column="TerminalVersionID")
    sub_service_level_version = models.ForeignKey(
        SubServiceLevelHistory, on_delete   =models.CASCADE, null=True, db_column="SubServiceLevelVersionID")
    cost_by_weight_break = models.TextField(
        null=False, blank=False, default="{}", db_column="Cost")
    pickup_delivery_count = models.IntegerField(
        null=True, blank=True, default=0, db_column="PickupDeliveryCount")
    rate_base = models.DecimalField(
        null=True, blank=True, decimal_places=6, max_digits=19, db_column="RateBase")
    rate_max = models.DecimalField(
        null=True, blank=True, decimal_places=6, max_digits=19, db_column="RateMax")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.broker_contract_cost_version_id)

    class Meta:
        index_together = (('broker_contract_cost', 'version_num'))
        verbose_name_plural = 'BrokerContractCost_History'
        db_table = "BrokerContractCost_History"


class CurrencyExchange(Delete):
    currency_exchange_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyExchangeID")
    cad_to_usd = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="CADtoUSD")
    usd_to_cad = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="USDtoCAD")

    def __str__(self):
        return str(self.currency_exchange_id)

    class Meta:
        verbose_name_plural = 'CurrencyExchange'
        db_table = "CurrencyExchange"


class CurrencyExchangeHistory(CommentUpdateDelete):
    currency_exchange_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyExchangeVersionID")
    currency_exchange = models.ForeignKey(
        CurrencyExchange, on_delete=models.CASCADE, db_column="CurrencyExchangeID")
    cad_to_usd = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="CADtoUSD")
    usd_to_cad = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="USDtoCAD")

    def __str__(self):
        return str(self.currency_exchange_version_id)

    class Meta:
        index_together = (('currency_exchange', 'version_num'))
        verbose_name_plural = 'CurrencyExchange_History'
        db_table = "CurrencyExchange_History"


class SpeedSheet(Delete):
    speed_sheet_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SpeedSheetID")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    margin = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="Margin")
    max_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MaxDensity")
    min_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MinDensity")

    def __str__(self):
        return str(self.speed_sheet_id)

    class Meta:
        verbose_name_plural = 'SpeedSheet'
        db_table = "SpeedSheet"


class SpeedSheetHistory(CommentUpdateDelete):
    speed_sheet_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SpeedSheetVersionID")
    speed_sheet = models.ForeignKey(
        SpeedSheet, on_delete=models.CASCADE, db_column="SpeedSheetID")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    margin = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="Margin")
    max_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MaxDensity")
    min_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MinDensity")

    def __str__(self):
        return str(self.speed_sheet_version_id)

    class Meta:
        index_together = (('speed_sheet', 'version_num'))
        verbose_name_plural = 'SpeedSheet_History'
        db_table = "SpeedSheet_History"


class TerminalServicePoint(Delete):
    terminal_service_point_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalServicePointID")
    extra_miles = models.IntegerField(
        null=False, blank=False, db_column="ExtraMiles")
    terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="TerminalID")
    service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, db_column="ServicePointID")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.terminal_service_point_id)

    class Meta:
        verbose_name_plural = 'TerminalServicePoint'
        db_table = "TerminalServicePoint"


class TerminalServicePointHistory(CommentUpdateDelete):
    terminal_service_point_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalServicePointVersionID")
    terminal_service_point = models.ForeignKey(
        TerminalServicePoint, on_delete=models.CASCADE, db_column="TerminalServicePointID")
    extra_miles = models.IntegerField(
        null=False, blank=False, db_column="ExtraMiles")
    terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, db_column="TerminalVersionID")
    service_point_version = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, db_column="ServicePointVersionID")
    legacy_id = models.BigIntegerField(null=True, blank=True, db_column="LegacyID")

    def __str__(self):
        return str(self.terminal_service_point_version_id)

    class Meta:
        index_together = (('terminal_service_point', 'version_num'))
        verbose_name_plural = 'TerminalServicePoint_History'
        db_table = "TerminalServicePoint_History"


class LaneCostWeightBreakLevel(Delete):
    weight_break_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakLevelID")
    weight_break_level_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="WeightBreakLevelName")
    weight_break_lower_bound = models.IntegerField(
        null=False, blank=False, db_column="WeightBreakLowerBound")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")

    def __str__(self):
        return str(self.weight_break_level_id)

    class Meta:
        verbose_name_plural = 'LaneCostWeightBreakLevel'
        db_table = "LaneCostWeightBreakLevel"


class LaneCostWeightBreakLevelHistory(CommentUpdateDelete):
    weight_break_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakLevelVersionID")
    weight_break_level = models.ForeignKey(
        LaneCostWeightBreakLevel, on_delete=models.CASCADE, db_column="WeightBreakLevelID")
    weight_break_level_name = models.CharField(
        max_length=50, unique=False, null=False, blank=False, db_column="WeightBreakLevelName")
    weight_break_lower_bound = models.IntegerField(
        null=False, blank=False, db_column="WeightBreakLowerBound")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")

    def __str__(self):
        return str(self.weight_break_level_version_id)

    class Meta:
        index_together = (('weight_break_level', 'version_num'))
        verbose_name_plural = 'LaneCostWeightBreakLevel_History'
        db_table = "LaneCostWeightBreakLevel_History"


class TerminalCostWeightBreakLevel(Delete):
    weight_break_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakLevelID")
    weight_break_level_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="WeightBreakLevelName")
    weight_break_lower_bound = models.IntegerField(
        null=False, blank=False, db_column="WeightBreakLowerBound")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")

    def __str__(self):
        return str(self.weight_break_level_id)

    class Meta:
        verbose_name_plural = 'TerminalCostWeightBreakLevel'
        db_table = "TerminalCostWeightBreakLevel"


class TerminalCostWeightBreakLevelHistory(CommentUpdateDelete):
    weight_break_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakLevelVersionID")
    weight_break_level = models.ForeignKey(
        TerminalCostWeightBreakLevel, on_delete=models.CASCADE, db_column="WeightBreakLevelID")
    weight_break_level_name = models.CharField(
        max_length=50, unique=False, null=False, blank=False, db_column="WeightBreakLevelName")
    weight_break_lower_bound = models.IntegerField(
        null=False, blank=False, db_column="WeightBreakLowerBound")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")

    def __str__(self):
        return str(self.weight_break_level_version_id)

    class Meta:
        index_together = (('weight_break_level', 'version_num'))
        verbose_name_plural = 'TerminalCostWeightBreakLevel_History'
        db_table = "TerminalCostWeightBreakLevel_History"


class SpotQuoteMargin(Delete):
    is_active = models.BooleanField(
        default=1, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        default=1, null=False, db_column="IsInactiveViewable")
    spot_quote_margin_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SpotQuoteMarginID")
    origin_province_id = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_column="OriginProvinceID", related_name="+")
    destination_province_id = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_column="DestinationProvinceID", related_name="+")
    service_level_id = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=True, db_column="ServiceLevelID")
    min_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="MinMargin")
    std_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="StdMargin")
    max_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="MaxMargin")
    updated_on = models.DateTimeField(auto_now_add=True, null=False, blank=False, db_column="UpdatedOn")

    def __str__(self):
        return str(self.spot_quote_margin_id)

    class Meta:
        verbose_name_plural = 'SpotQuoteMargin'
        db_table = "SpotQuoteMargin"


class SpotQuoteMarginHistory(CommentUpdateDelete):
    is_active = models.BooleanField(
        default=1, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        default=1, null=False, db_column="IsInactiveViewable")
    spot_quote_margin_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SpotQuoteMarginVersionID")
    spot_quote_margin_id = models.ForeignKey(
        SpotQuoteMargin, on_delete=models.CASCADE, null=True, db_column="SpotQuoteMarginID")
    origin_province_version_id = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, null=True, db_column="OriginProvinceVersionID", related_name="+")
    destination_province_version_id = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, null=True, db_column="DestinationProvinceVersionID", related_name="+")
    service_level_version_id = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, null=True, db_column="ServiceLevelVersionID")
    min_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="MinMargin")
    std_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="StdMargin")
    max_margin = models.CharField(
        max_length=40, null=False, blank=False, db_column="MaxMargin")
    updated_on = models.DateTimeField(db_column='UpdatedOn', default=None)

    def __str__(self):
        return str(self.spot_quote_margin_version_id)

    class Meta:
        index_together = (('spot_quote_margin_id', 'version_num'))
        verbose_name_plural = 'SpotQuoteMargin_History'
        db_table = "SpotQuoteMargin_History"

class GriReview(Delete):
    gri_review_id = models.BigAutoField(primary_key=True, null=False, db_column="GriReviewID")
    service_level = models.ForeignKey(ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    expiry_on = models.DateTimeField(null=True, blank=True, db_column="ExpiryOn") # Date GRI Batch item expires (STOPPED)
    start_on = models.DateTimeField(null=True, blank=True, db_column="StartOn") # Date GRI Batch starts (becomes IN PROGRESS)
    uni_status = models.TextField(default="NEW", null=False, blank=False, db_column="UniStatus")
    gri_amount = models.FloatField(null=True, default=0, db_column="GriAmount")
    gri_percentage = models.FloatField(null=True, default=False, db_column="GriPercentage")
    min_revenue = models.FloatField(null=True, default=False, db_column="MinRevenue")
    max_revenue = models.FloatField(null=True, default=False, db_column="MaxRevenue")
    min_operating_ratio = models.FloatField(null=True, default=False, db_column="MinOperatingRatio")
    max_operating_ratio = models.FloatField(null=True, default=False, db_column="MaxOperatingRatio")
    current_rate_base = models.CharField(max_length=100, null=True, blank=True, db_column="CurrentRateBase")
    current_effective_date = models.DateTimeField(null=True, blank=True, db_column="CurrentEffectiveDate") #Rate base param
    current_tm_ratebase = models.CharField(max_length=100, null=True, blank=True, db_column="CurrentTmRatebase")
    future_rate_base = models.CharField(max_length=100, null=True, blank=True, db_column="FutureRateBase")
    future_effective_date = models.DateTimeField(null=True, blank=True, db_column="FutureEffectiveDate") #Rate base param
    future_tm_ratebase = models.CharField(max_length=100, null=True, blank=True, db_column="FutureTmRatebase")
    new_effective_date = models.DateTimeField(null=True, blank=True, db_column="NewEffectiveDate") # Effective date for Created GRI Tariff
    new_expiry_date = models.DateTimeField(null=True, blank=True, db_column="NewExpiryDate") #Expiry date for created GRI Tqriff
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    created_on = models.DateTimeField(auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(auto_now_add=True, null=False, blank=False, db_column="UpdatedOn")

    def __str__(self):
        return str(self.gri_review_id)

    class Meta:
        verbose_name_plural = 'GriReview'
        db_table = 'GriReview'
        # TODO uncomment the line bellow, after upgrading to latest version of Django,
        #  in order to create unique constraint (task PAC-2052). See task's comment in Jira.
        # constraints = [models.UniqueConstraint(fields=['expiry_on', 'service_level'], name='unique_gri')]


class GriReviewHistory(CommentUpdateDelete):
    gri_review_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="GriReviewVersionID")
    gri_review = models.ForeignKey(
        GriReview, on_delete=models.CASCADE, db_column="GriReviewID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=True, db_column="ServiceLevelID")
    expiry_on = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, db_column="ExpiryOn")
    start_on = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, db_column="StartOn")
    uni_status = models.TextField(
        default="NEW", null=False, blank=False, db_column="UniStatus")
    gri_amount = models.FloatField(
        null=True, default=0, db_column="GriAmount")
    gri_percentage = models.FloatField(
        null=True, default=True, db_column="GriPercentage")
    min_revenue = models.FloatField(
        null=True, default=True, db_column="MinRevenue")
    max_revenue = models.FloatField(
        null=True, default=True, db_column="MaxRevenue")
    min_operating_ratio = models.FloatField(
        null=True, default=True, db_column="MinOperatingRatio")
    max_operating_ratio = models.FloatField(
        null=True, default=True, db_column="MaxOperatingRatio")
    current_rate_base = models.CharField(
        max_length=100, null=True, blank=True, db_column="CurrentRateBase")
    current_effective_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, db_column="CurrentEffectiveDate")
    current_tm_ratebase = models.CharField(
        max_length=100, null=True, blank=True, db_column="CurrentTmRatebase")
    future_rate_base = models.CharField(
        max_length=100, null=True, blank=True, db_column="FutureRateBase")
    future_effective_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, db_column="FutureEffectiveDate")
    future_tm_ratebase = models.CharField(
        max_length=100, null=True, blank=True, db_column="FutureTmRatebase")
    new_effective_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, db_column="NewEffectiveDate")
    new_expiry_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=False, db_column="NewExpiryDate")

    # created_by = models.ForeignKey(
    #     User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="UpdatedOn")

    def __str__(self):
        return str(self.gri_review_version_id)

    class Meta:
        index_together = (('gri_review', 'version_num'))
        verbose_name_plural = 'GriReview_History'
        db_table = 'GriReview_History'

class EngineOperation(models.Model):
    OperationID = models.BigAutoField(
        primary_key=True, null=False, db_column="OperationID")
    OperationName = models.CharField(
        max_length=50, null=False, blank=False, db_column="OperationName")
    class Meta:
        db_table = 'EngineOperation'

class EngineQueue(models.Model):
    EngineQueueID = models.BigAutoField(
        primary_key=True, null=False, db_column="EngineQueueID")
    OperationID = models.ForeignKey(
        EngineOperation, on_delete=models.CASCADE, db_column="OperationID", related_name="+")
    RequestID = models.BigIntegerField(blank=True, db_column='RequestID'),
    OperationBody = models.CharField(max_length=4000, blank=False, db_column='OperationBody')
    Description = models.CharField(max_length=200, blank=False, default='Operation pending ...', db_column='Description')
    DueDate = models.DateTimeField(blank=False, default=datetime.now, db_column="DueDate")
    CompletedOn = models.DateTimeField(blank=True, db_column="CompletedOn")
    Completed = models.BooleanField(blank=False, default=False, db_column="Completed")
    Success = models.BooleanField(blank=False, default=False, db_column="Success")
    InProgress = models.BooleanField(blank=False, default=False, db_column="InProgress")
    Recurring = models.BooleanField(blank=False, default=False, db_column="Recurring")
    RecurringPattern = models.CharField(max_length=200, blank=True, default='{"pattern":"daily"}', db_column='RecurringPattern')
    RequestedBy = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="RequestedBy", related_name="+")
    class Meta:
        db_table = 'EngineQueue'

@receiver(models.signals.post_save, sender=TerminalCost)
@receiver(models.signals.post_save, sender=UnitConversion)
@receiver(models.signals.post_save, sender=DockRoute)
@receiver(models.signals.post_save, sender=LaneRoute)
@receiver(models.signals.post_save, sender=LaneCost)
@receiver(models.signals.post_save, sender=LegCost)
@receiver(models.signals.post_save, sender=BrokerContractCost)
@receiver(models.signals.post_save, sender=CurrencyExchange)
@receiver(models.signals.post_save, sender=SpeedSheet)
@receiver(models.signals.post_save, sender=TerminalServicePoint)
@receiver(models.signals.post_save, sender=GriReview)
def post_save_instance(sender, instance, created, **kwargs):
    from pac.helpers.functions import create_instance_history
    create_instance_history(sender, instance, globals())

# TODO:
# base_version for history, change revert accordingly
