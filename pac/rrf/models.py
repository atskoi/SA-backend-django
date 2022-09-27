import uuid

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone

from core.models import User, UserHistory
from pac.helpers.base import CommentUpdateDelete, Delete
from pac.models import (Account, AccountHistory, BasingPoint,
                        BasingPointHistory, Country,
                        CountryHistory, Notification, NotificationHistory,
                        PostalCode, PostalCodeHistory, Province,
                        ProvinceHistory, Region, RegionHistory, ServiceLevel,
                        ServiceLevelHistory, ServiceOffering,
                        ServiceOfferingHistory, ServicePoint,
                        ServicePointHistory, SubServiceLevel,
                        SubServiceLevelHistory, Terminal, TerminalHistory,
                        Unit, UnitHistory, WeightBreakHeader, WeightBreakHeaderHistory)
from datetime import datetime

class AccountTree(Delete):
    account_tree_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountTreeID")
    account = models.OneToOneField(
        Account, on_delete=models.CASCADE, db_column="AccountID", related_name="+")
    parent_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, db_column="ParentAccountID", related_name="+")

    def __str__(self):
        return str(self.account_tree_id)

    class Meta:
        verbose_name_plural = 'AccountTree'
        db_table = 'AccountTree'


class AccountTreeHistory(CommentUpdateDelete):
    account_tree_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountTreeVersionID")
    account_tree = models.ForeignKey(
        AccountTree, on_delete=models.CASCADE, db_column="AccountTreeID")
    account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, db_column="AccountVersionID", related_name="+")
    parent_account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, null=True, db_column="ParentAccountVersionID", related_name="+")

    def __str__(self):
        return str(self.account_tree_version_id)

    class Meta:
        index_together = (('account_tree', 'version_num'))
        verbose_name_plural = 'AccountTree_History'
        db_table = 'AccountTree_History'


class Currency(Delete):
    currency_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyID")
    currency_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="CurrencyName")
    currency_code = models.CharField(
        max_length=3, unique=True, null=False, blank=False, db_column="CurrencyCode")

    def __str__(self):
        return str(self.currency_id)

    class Meta:
        verbose_name_plural = 'Currency'
        db_table = 'Currency'


class CurrencyHistory(CommentUpdateDelete):
    currency_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyVersionID")
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, db_column="CurrencyID")
    currency_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="CurrencyName")
    currency_code = models.CharField(
        max_length=3, null=False, blank=False, db_column="CurrencyCode")

    def __str__(self):
        return str(self.currency_version_id)

    class Meta:
        index_together = (('currency', 'version_num'))
        verbose_name_plural = 'Currency_History'
        db_table = 'Currency_History'


class Customer(Delete):
    customer_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CustomerID")
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, db_column="AccountID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, null=True, db_column="ServicePointID")
    customer_name = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerName")
    customer_alias = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAlias")
    customer_address_line_1 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAddressLine1")
    customer_address_line_2 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAddressLine2")
    postal_code = models.CharField(
        max_length=10, unique=False, null=True, blank=False, db_column="PostalCode")
    contact_name = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="ContactName")
    contact_title = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="ContactTitle")
    phone = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Phone")
    email = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Email")
    website = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Website")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.customer_id)

    class Meta:
        verbose_name_plural = 'Customer'
        db_table = 'Customer'


class CustomerHistory(CommentUpdateDelete):
    customer_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CustomerVersionID")
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, db_column="CustomerID")
    account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, null=True, db_column="AccountVersionID")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, db_column="ServiceLevelVersionID")
    service_point_version = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, null=True, db_column="ServicePointVersionID")
    customer_name = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerName")
    customer_alias = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAlias")
    customer_address_line_1 = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAddressLine1")
    customer_address_line_2 = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAddressLine2")
    postal_code = models.CharField(
        max_length=10, null=True, blank=False, db_column="PostalCode")
    contact_name = models.CharField(
        max_length=100, null=True, blank=False, db_column="ContactName")
    contact_title = models.CharField(
        max_length=100, null=True, blank=False, db_column="ContactTitle")
    phone = models.CharField(
        max_length=100, null=True, blank=False, db_column="Phone")
    email = models.CharField(
        max_length=100, null=True, blank=False, db_column="Email")
    website = models.CharField(
        max_length=100, null=True, blank=False, db_column="Website")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.customer_version_id)

    class Meta:
        index_together = (('customer', 'version_num'))
        verbose_name_plural = 'Customer_History'
        db_table = 'Customer_History'


class Language(Delete):
    language_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LanguageID")
    language_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="LanguageName")
    language_code = models.CharField(
        max_length=2, unique=True, null=False, blank=False, db_column="LanguageCode")

    def __str__(self):
        return str(self.language_id)

    class Meta:
        verbose_name_plural = 'Language'
        db_table = 'Language'


class LanguageHistory(CommentUpdateDelete):
    language_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LanguageVersionID")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, db_column="LanguageID")
    language_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="LanguageName")
    language_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="LanguageCode")

    def __str__(self):
        return str(self.language_version_id)

    class Meta:
        index_together = (('language', 'version_num'))
        verbose_name_plural = 'Language_History'
        db_table = 'Language_History'


class RequestStatusType(Delete):
    request_status_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusTypeID")
    request_status_type_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="RequestStatusTypeName")
    def __str__(self):
        return str(self.request_status_type_id)

    class Meta:
        verbose_name_plural = 'RequestStatusType'
        db_table = 'RequestStatusType'


class RequestStatusTypeHistory(CommentUpdateDelete):
    request_status_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusTypeVersionID")
    request_status_type = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, db_column="RequestStatusTypeID")
    request_status_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestStatusTypeName")

    def __str__(self):
        return str(self.request_status_type_version_id)

    class Meta:
        index_together = (('request_status_type', 'version_num'))
        verbose_name_plural = 'RequestStatusType_History'
        db_table = 'RequestStatusType_History'


class FreightClass(Delete):
    freight_class_id = models.BigAutoField(
        primary_key=True, null=False, db_column="FreightClassID")
    freight_class_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="FreightClassName")

    def __str__(self):
        return str(self.freight_class_id)

    class Meta:
        verbose_name_plural = 'FreightClass'
        db_table = 'FreightClass'


class FreightClassHistory(CommentUpdateDelete):
    freight_class_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="FreightClassVersionID")
    freight_class = models.ForeignKey(
        FreightClass, on_delete=models.CASCADE, db_column="FreightClassID")
    freight_class_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="FreightClassName")

    def __str__(self):
        return str(self.freight_class_version_id)

    class Meta:
        index_together = (('freight_class', 'version_num'))
        verbose_name_plural = 'FreightClass_History'
        db_table = 'FreightClass_History'


class RateBase(Delete):
    rate_base_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RateBaseID")
    rate_base_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RateBaseName")
    product_number = models.CharField(
        max_length=50, null=True, blank=False, db_column="ProductNumber")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")
    release = models.CharField(
        max_length=50, null=True, blank=False, db_column="Release")
    effective_date = models.DateField(
        max_length=50, null=True, blank=False, db_column="EffectiveDate")

    def __str__(self):
        return str(self.rate_base_id)

    class Meta:
        verbose_name_plural = 'RateBase'
        db_table = 'RateBase'


class RateBaseHistory(CommentUpdateDelete):
    rate_base_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RateBaseVersionID")
    rate_base = models.ForeignKey(
        RateBase, on_delete=models.CASCADE, db_column="RateBaseID")
    rate_base_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RateBaseName")
    product_number = models.CharField(
        max_length=50, null=True, blank=False, db_column="ProductNumber")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")
    release = models.CharField(
        max_length=50, null=True, blank=False, db_column="Release")
    effective_date = models.DateField(
        max_length=50, null=True, blank=False, db_column="EffectiveDate")

    def __str__(self):
        return str(self.rate_base_version_id)

    class Meta:
        index_together = (('rate_base', 'version_num'))
        verbose_name_plural = 'RateBase_History'
        db_table = 'RateBase_History'


class EquipmentType(Delete):
    equipment_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeID")
    equipment_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="EquipmentTypeName")
    equipment_type_code = models.CharField(
        max_length=10, null=False, blank=False, db_column="EquipmentTypeCode")

    def __str__(self):
        return str(self.equipment_type_id)

    class Meta:
        verbose_name_plural = 'EquipmentType'
        unique_together = (('equipment_type_name', 'equipment_type_code'))
        db_table = 'EquipmentType'


class EquipmentTypeHistory(CommentUpdateDelete):
    equipment_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeVersionID")
    equipment_type = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, db_column="EquipmentTypeID")
    equipment_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="EquipmentTypeName")
    equipment_type_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="EquipmentTypeCode")

    def __str__(self):
        return str(self.equipment_type_version_id)

    class Meta:
        index_together = (('equipment_type', 'version_num'))
        verbose_name_plural = 'EquipmentType_History'
        db_table = 'EquipmentType_History'


class EquipmentTypeMap(Delete):
    equipment_type_map_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeMapID")
    equipment_type_id = models.ForeignKey(
        EquipmentType, db_column='EquipmentTypeID', on_delete=models.CASCADE, related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', default=None)

    def __str__(self):
        return str(self.equipment_type_map_id)

    class Meta:
        verbose_name_plural = 'EquipmentTypeMap'
        db_table = 'EquipmentTypeMap'


class EquipmentTypeMapHistory(CommentUpdateDelete):
    equipment_type_map_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeMapVersionID")
    equipment_type_map = models.ForeignKey(
        EquipmentTypeMap, on_delete=models.CASCADE, db_column="EquipmentTypeMapID")
    equipment_type_version_id = models.ForeignKey(
        EquipmentTypeHistory, db_column='EquipmentTypeVersionID', on_delete=models.CASCADE, related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', default=None)

    def __str__(self):
        return str(self.equipment_type_map_version_id)

    class Meta:
        index_together = (('equipment_type_map', 'version_num'))
        verbose_name_plural = 'EquipmentTypeMap_History'
        db_table = 'EquipmentTypeMap_History'


class Zone(Delete):
    zone_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ZoneID")
    zone_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="ZoneName")
    zone_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="ZoneCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.zone_id)

    class Meta:
        verbose_name_plural = 'Zone'
        db_table = 'Zone'


class ZoneHistory(CommentUpdateDelete):
    zone_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ZoneVersionID")
    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=False, db_column="ZoneID")
    zone_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="ZoneName")
    zone_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="ZoneCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.zone_version_id)

    class Meta:
        index_together = (('zone', 'version_num'))
        verbose_name_plural = 'Zone_History'
        db_table = 'Zone_History'


class RequestType(Delete):
    request_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestTypeID")
    request_type_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="RequestTypeName")
    apply_to_customer_under_review = models.BooleanField(
        null=False, default=True, db_column="ApplyToCustomerUnderReview")
    apply_to_revision = models.BooleanField(
        null=False, default=True, db_column="ApplyToRevision")
    allow_sales_commitment = models.BooleanField(
        null=False, default=True, db_column="AllowSalesCommitment")

    def __str__(self):
        return str(self.request_type_id)

    class Meta:
        verbose_name_plural = 'RequestType'
        db_table = 'RequestType'


class RequestTypeHistory(CommentUpdateDelete):
    request_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestTypeVersionID")
    request_type = models.ForeignKey(
        RequestType, on_delete=models.CASCADE, db_column="RequestTypeID")
    request_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestTypeName")
    apply_to_customer_under_review = models.BooleanField(
        null=False, default=True, db_column="ApplyToCustomerUnderReview")
    apply_to_revision = models.BooleanField(
        null=False, default=True, db_column="ApplyToRevision")
    allow_sales_commitment = models.BooleanField(
        null=False, default=True, db_column="AllowSalesCommitment")

    def __str__(self):
        return str(self.request_type_version_id)

    class Meta:
        index_together = (('request_type', 'version_num'))
        verbose_name_plural = 'RequestType_History'
        db_table = 'RequestType_History'


class Request(Delete):
    request_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestID")
    request_code = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestCode")
    request_major_version = models.IntegerField(null=False, default=1, db_column="RequestMajorVersion")
    initiated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="InitiatedOn")
    initiated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="InitiatedBy", related_name="+")
    submitted_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="SubmittedOn")
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="SubmittedBy", blank=True, null=True, default=None, related_name="+")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_review = models.BooleanField(
        null=False, default=False, db_column="IsReview")
    request_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="RequestOwner", default=None, blank=True, null=True, related_name="+")
    uni_type = models.TextField(
        null=True, blank=False, db_column="UniType")
    speedsheet_name = models.TextField(
        null=True, blank=True, db_column="SpeedsheetName")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageID")
    request_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSourceID")
    sales_representative = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="SalesRepresentativeID", related_name="+")
    pricing_analyst = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="PricingAnalystID", related_name="+")
    credit_analyst = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="CreditAnalystID", related_name="+")
    current_editor = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="CurrentEditorID", related_name="+")
    request_status_type = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, null=False, default=1, db_column="RequestStatusTypeID", related_name="+")
    pricing_running = models.BooleanField(
        default=0, db_column="PricingRunning")
    cost_plus_status = models.TextField(
        db_column='CostPlusStatus', max_length=20, null=True)
    carrier_status = models.TextField(
        db_column='CarrierStatus', max_length=20, null=True)
    sales_status = models.TextField(
        db_column='SalesStatus', max_length=20, null=True)
    pricing_opened = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PricingOpened")
    pricing_assigned = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PricingAssigned")
    approver = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, db_column="ApproverID", related_name="+")
    new_lanes_only = models.BooleanField(null=False, default=False, db_column="NewLanesOnly")

    def __str__(self):
        return str(self.request_id)

    class Meta:
        verbose_name_plural = 'Request'
        db_table = 'Request'


class RequestHistory(CommentUpdateDelete):
    request_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestVersionID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    request_code = models.CharField(
        max_length=32, unique=False, null=False, blank=False, db_column="RequestCode")
    request_major_version = models.IntegerField(null=False, default=1, db_column="RequestMajorVersion")
    initiated_on = models.DateTimeField(
        auto_now_add=False, null=False, db_column="InitiatedOn")
    initiated_by_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, blank=True, db_column="InitiatedByVersionID", related_name="+")
    request_owner_version_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="RequestOwnerVersionID", blank=True, null=True, related_name="+")
    submitted_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="SubmittedOn")
    submitted_by_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, blank=True, null=True, db_column="SubmittedByVersionID", related_name="+")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_review = models.BooleanField(
        null=False, default=False, db_column="IsReview")
    uni_type = models.TextField(null=True, blank=False, db_column="UniType")
    speedsheet_name = models.TextField(null=True, blank=True, db_column="SpeedsheetName")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageVersionID")
    request_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSourceID")
    sales_representative_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="SalesRepresentativeVersionID", related_name="+")
    pricing_analyst_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="PricingAnalystVersionID", related_name="+")
    credit_analyst_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="CreditAnalystVersionID", related_name="+")
    current_editor_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="CurrentEditorVersionID", related_name="+")
    request_status_type_version = models.ForeignKey(
        RequestStatusTypeHistory, on_delete=models.CASCADE, null=False, blank=True, default=1, db_column="RequestStatusTypeVersionID", related_name="+")
    pricing_running = models.BooleanField(
        default=0, db_column="PricingRunning")
    cost_plus_status = models.TextField(
        db_column='CostPlusStatus', max_length=20, null=True)
    carrier_status = models.TextField(
        db_column='CarrierStatus', max_length=20, null=True)
    sales_status = models.TextField(
        db_column='SalesStatus', max_length=20, null=True)
    pricing_opened = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PricingOpened")
    pricing_assigned = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PricingAssigned")
    approver_version = models.ForeignKey(
            UserHistory, on_delete=models.CASCADE, null=True, blank=True, db_column="ApproverVersionID", related_name="+")
    new_lanes_only = models.BooleanField(null=False, default=False, db_column="NewLanesOnly")

    def __str__(self):
        return str(self.request_version_id)

    class Meta:
        index_together = (('request', 'version_num'))
        verbose_name_plural = 'Request_History'
        db_table = 'Request_History'

class RequestInformation(Delete):
    request_information_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestInformationID")
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, db_column="CustomerID")
    request_type = models.ForeignKey(
        RequestType, on_delete=models.CASCADE, null=True, db_column="RequestTypeID")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageID")
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, null=True, db_column="CurrencyID")
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=True, db_column="RequestID")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_new_business = models.BooleanField(
        null=True, default=True, db_column="IsNewBusiness")
    priority = models.IntegerField(
        null=True, blank=False, db_column="Priority")
    effective_date = models.DateField(null=True, blank=False, db_column="EffectiveDate")
    expiry_date = models.DateField(null=True, blank=False, db_column="ExpiryDate")

    def __str__(self):
        return str(self.request_information_id)

    class Meta:
        verbose_name_plural = 'RequestInformation'
        db_table = 'RequestInformation'


class RequestInformationHistory(CommentUpdateDelete):
    request_information_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestInformationVersionID")
    request_information = models.ForeignKey(
        RequestInformation, on_delete=models.CASCADE, db_column="RequestInformationID")
    customer_version = models.ForeignKey(
        CustomerHistory, on_delete=models.CASCADE, db_column="CustomerVersionID")
    request_type_version = models.ForeignKey(
        RequestTypeHistory, on_delete=models.CASCADE, null=True, db_column="RequestTypeVersionID")
    language_version = models.ForeignKey(
        LanguageHistory, on_delete=models.CASCADE, null=True, db_column="LanguageVersionID")
    currency_version = models.ForeignKey(
        CurrencyHistory, on_delete=models.CASCADE, null=True, db_column="CurrencyVersionID")
    request_version_id = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, null=True, db_column="RequestVersionID")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_new_business = models.BooleanField(
        null=True, default=True, db_column="IsNewBusiness")
    priority = models.IntegerField(
        null=True, blank=False, db_column="Priority")
    effective_date = models.DateField(null=True, blank=False, db_column="EffectiveDate")
    expiry_date = models.DateField(null=True, blank=False, db_column="ExpiryDate")

    def __str__(self):
        return str(self.request_information_version_id)

    class Meta:
        index_together = (('request_information', 'version_num'))
        verbose_name_plural = 'RequestInformation_History'
        db_table = 'RequestInformation_History'


class Commodity(Delete):
    commodity_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CommodityID")
    freight_class = models.ForeignKey(
        FreightClass, on_delete=models.CASCADE, db_column="FreightClassID")
    commodity_name = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityName")
    commodity_code = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityCode")

    def __str__(self):
        return str(self.commodity_id)

    class Meta:
        verbose_name_plural = 'Commodity'
        db_table = 'Commodity'


class CommodityHistory(CommentUpdateDelete):
    commodity_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CommodityVersionID")
    commodity_id = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, db_column="CommodityID")
    freight_class_version_id = models.ForeignKey(
        FreightClassHistory, on_delete=models.CASCADE, db_column="FreightClassVersionID")
    commodity_name = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityName")
    commodity_code_history = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityCode")

    def __str__(self):
        return str(self.commodity_id)

    class Meta:
        index_together = (("commodity_id", "version_num"))
        verbose_name_plural = 'Commodity_History'
        db_table = 'Commodity_History'


class Comment(Delete):
    comment_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CommentID")
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    request_major_version = models.IntegerField(db_column='RequestMajorVersion', null=False, default=1)
    tag = models.CharField(db_column='Tag', max_length=100, null=True)
    request_status_type_id = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, null=False, default=1, db_column="RequestStatusTypeID",
        related_name="+")
    content = models.TextField(db_column='Content', null=False, blank=False)
    parent_comment_id = models.BigIntegerField(null=True, blank=True, db_column="ParentCommentID")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
    created_by = models.CharField(db_column='CreatedBy', max_length=100, null=True)

    def __str__(self):
        return str(self.comment_id)

    class Meta:
        db_table = 'Comment'


class AccChargeBehavior(Delete):
    acc_charge_behavior_id = models.BigAutoField(
        primary_key=True, db_column="AccChargeBehaviorID", serialize=False)
    tm_charge_behavior_code = models.TextField(
        max_length=40, null=True, blank=False, db_column="TMChargeBehaviorCode", default=None)
    acc_charge_behavior = models.TextField(
        max_length=10, null=True, blank=False, db_column="AccChargeBehavior", default=None)

    def __str__(self):
        return str(self.acc_charge_behavior_id)

    class Meta:
        verbose_name_plural = 'AccChargeBehavior'
        db_table = 'AccChargeBehavior'


class AccChargeBehaviorHistory(Delete):
    version_num = models.IntegerField(
        null=True, db_column="VersionNum", default=None)
    is_latest_version = models.BooleanField(
        default=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        default=None, db_column="UpdatedOn")
    updated_by = models.TextField(
        default=None, db_column="UpdatedBy")
    base_version = models.IntegerField(
        db_column="BaseVersion", default=None)
    comments = models.TextField(
        default=None, db_column="Comments")
    acc_charge_behavior_version_id = models.BigAutoField(
        db_column='AccChargeBehaviorVersionID', primary_key=True, serialize=False)
    tm_charge_behavior_code = models.TextField(
        db_column='TMChargeBehaviorCode', max_length=40, null=True, default=None)
    acc_charge_behavior_id = models.ForeignKey(
        AccChargeBehavior, db_column='AccChargeBehaviorID', on_delete=models.CASCADE)
    acc_charge_behavior = models.TextField(db_column='AccChargeBehavior', max_length=10, null=True, default=None)

    def __str__(self):
        return str(self.acc_charge_behavior_version_id)

    class Meta:
        index_together = (("acc_charge_behavior_id", "version_num"))
        verbose_name_plural = 'AccChargeBehavior_History'
        db_table = 'AccChargeBehavior_History'


class AccRangeType(Delete):
    acc_range_type_id = models.BigAutoField(db_column='AccRangeTypeID', primary_key=True, serialize=False)
    tm_range_type_code = models.TextField(db_column='TMRangeTypeCode', max_length=10, null=True, default=None)
    tm_range_type = models.TextField(db_column='TMRangeType', max_length=40, null=True, default=None)

    def __str__(self):
        return str(self.acc_range_type_id)

    class Meta:
        verbose_name_plural = 'AccRangeType'
        db_table = 'AccRangeType'


class AccRangeTypeHistory(Delete):
    version_num = models.IntegerField(db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(db_column='UpdatedOn', default=None)
    updated_by = models.TextField(db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(db_column='BaseVersion', default=None)
    comments = models.TextField(db_column='Comments', default=None)
    acc_range_type_id = models.ForeignKey(
        AccRangeType, db_column='AccRangeTypeID', on_delete=models.CASCADE, related_name='+')
    acc_range_type_version_id = models.BigAutoField(
        db_column='AccRangeTypeVersionID', primary_key=True, serialize=False)
    tm_range_type = models.TextField(db_column='TMRangeType', max_length=40, null=True, default=None)
    tm_range_type_code = models.TextField(db_column='TMRangeTypeCode', max_length=10, null=True, default=None)

    def __str__(self):
        return str(self.acc_range_type_version_id)

    class Meta:
        index_together = (("acc_range_type_id", "version_num"))
        verbose_name_plural = 'AccRangeType_History'
        db_table = 'AccRangeType_History'


class FreeTime(Delete):
    free_time_id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name='FreeTimeID')
    min_break = models.DecimalField(
        db_column='MinBreak', decimal_places=6, max_digits=19, null=True, default=None)
    max_break = models.DecimalField(
        db_column='MaxBreak', decimal_places=6, max_digits=19, null=True, default=None)
    tm_detention_id = models.BigIntegerField(
        db_column='TMDetentionID', null=True, default=None)
    free_time = models.IntegerField(
        db_column='FreeTime', null=True, default=None)
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=10, null=True, default=None)

    def __str__(self):
        return str(self.free_time_id)

    class Meta:
        verbose_name_plural = 'FreeTime'
        db_table = 'FreeTime'


class FreeTimeHistory(Delete):
    version_num = models.IntegerField(db_column='VersionNum', null=True, default=None)
    is_latest_version = models.BooleanField(db_column='IsLatestVersion', null=True, default=False)
    updated_on = models.DateTimeField(db_column='UpdatedOn', null=True, default=None)
    updated_by = models.TextField(db_column='UpdatedBy', null=True, default=None)
    base_version = models.IntegerField(db_column='BaseVersion', null=True, default=None)
    comments = models.TextField(db_column='Comments', null=True, default=None)
    free_time_version_id = models.BigAutoField(
        db_column='FreeTimeVersionID', primary_key=True, serialize=False)
    min_break = models.DecimalField(
        db_column='MinBreak', decimal_places=6, max_digits=19, null=True, default=None)
    max_break = models.DecimalField(
        db_column='MaxBreak', decimal_places=6, max_digits=19, null=True, default=None)
    free_time_id = models.ForeignKey(
        FreeTime, db_column='FreeTimeID', on_delete=models.CASCADE, related_name='+')
    tm_detention_id = models.BigIntegerField(
        db_column='TMDetentionID', null=True, default=None)
    free_time = models.IntegerField(
        db_column='FreeTime', null=True, default=None)
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=10, null=True, default=None)

    def __str__(self):
        return str(self.free_time_version_id)

    class Meta:
        index_together = (("free_time_id", "version_num"))
        verbose_name_plural = 'FreeTime_History'
        db_table = 'FreeTime_History'


class AccFactor(Delete):
    acc_factor_id = models.BigAutoField(db_column='AccFactorID', primary_key=True, serialize=False)
    tm_acc_factor_code = models.TextField(db_column='TMAccFactorCode', max_length=10, null=True, default=None)
    acc_factor = models.TextField(db_column='AccFactor', max_length=40, null=True, default=None)

    def __str__(self):
        return str(self.acc_factor_id)

    class Meta:
        verbose_name_plural = 'AccFactor'
        db_table = 'AccFactor'


class AccFactorHistory(Delete):
    version_num = models.IntegerField(db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(db_column='UpdatedOn', default=None)
    updated_by = models.TextField(db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(db_column='BaseVersion', default=None)
    comments = models.TextField(db_column='Comments', default=None)
    acc_factor_version_id = models.BigAutoField(db_column='AccFactorVersionID', primary_key=True, serialize=False)
    acc_factor = models.TextField(db_column='AccFactor', max_length=40, null=True, default=None)
    tm_acc_factor_code = models.TextField(db_column='TMAccFactorCode', max_length=10, null=True, default=None)
    acc_factor_id = models.ForeignKey(
        AccFactor, db_column='AccFactorID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.acc_factor_version_id)

    class Meta:
        index_together = (("acc_factor_id", "version_num"))
        verbose_name_plural = 'AccFactor_History'
        db_table = 'AccFactor_History'


class AccessorialHeader(Delete):
    acc_header_id = models.BigAutoField(
        db_column='AccHeaderID', primary_key=True, serialize=False)
    tmacc_charge_code = models.TextField(
        db_column='TMAccChargeCode', max_length=10, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    business_grouping = models.TextField(
        db_column='BusinessGrouping', null=True, default=None)
    acc_charge_behavior_id = models.ForeignKey(
        AccChargeBehavior, db_column='AccChargeBehaviorID', on_delete=models.CASCADE, related_name='+')
    acc_range_field_id = models.ForeignKey(
        AccRangeType, db_column='AccRangeFieldID', null=True, on_delete=models.CASCADE, related_name='+')
    currency_id = models.ForeignKey(
        Currency, db_column='CurrencyID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.acc_header_id)

    class Meta:
        verbose_name_plural = 'AccessorialHeader'
        db_table = 'AccessorialHeader'


class AccessorialHeaderHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')
    acc_header_version_id = models.BigAutoField(
        db_column='AccHeaderVersionID', primary_key=True, serialize=False)
    tmacc_charge_code = models.TextField(
        db_column='TMAccChargeCode', max_length=10, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    business_grouping = models.TextField(
        db_column='BusinessGrouping', null=True, default=None)
    acc_charge_behavior_version_id = models.ForeignKey(
        AccChargeBehaviorHistory, db_column='AccChargeBehaviorVersionID', on_delete=models.CASCADE, related_name='+')
    acc_range_field_version_id = models.ForeignKey(
        AccRangeTypeHistory, db_column='AccRangeFieldVersionID', null=True, on_delete=models.CASCADE, related_name='+')
    currency_version_id = models.ForeignKey(
        CurrencyHistory, db_column='CurrencyVersionID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.acc_header_version_id)

    class Meta:
        index_together = (("acc_header_id", "version_num"))
        verbose_name_plural = 'AccessorialHeader_History'
        db_table = 'AccessorialHeader_History'


class ServiceClassMap(Delete):
    service_class_map_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceClassMapID")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=False, db_column="SubServiceLevelID", default=8)
    tmid = models.IntegerField(
        db_column='TMID', default=None)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.service_class_map_id)

    class Meta:
        verbose_name_plural = 'ServiceClassMap'
        db_table = 'ServiceClassMap'


class ServiceClassMapHistory(CommentUpdateDelete):
    service_class_map_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceClassMapVersionID")
    service_class_map = models.ForeignKey(
        ServiceClassMap, on_delete=models.CASCADE, db_column="ServiceClassMapID")
    sub_service_level_version = models.ForeignKey(
        SubServiceLevelHistory, on_delete=models.CASCADE, db_column="SubServiceLevelVersionID", default=8)
    tmid = models.IntegerField(
        db_column='TMID', default=None)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.service_class_map_version_id)

    class Meta:
        index_together = (('service_class_map', 'version_num'))
        verbose_name_plural = 'ServiceClassMap_History'
        db_table = 'ServiceClassMap_History'


class PointType(Delete):
    point_type_id = models.BigAutoField(db_column='PointTypeID', primary_key=True, serialize=False)
    point_type_name = models.TextField(db_column='PointTypeName', max_length=4000, null=False, default=None)
    point_type_order_id = models.IntegerField(db_column='PointTypeOrderID', null=False, default=None)

    def __str__(self):
        return str(self.point_type_id)

    class Meta:
        verbose_name_plural = 'PointType'
        db_table = 'PointType'


class PointTypeHistory(CommentUpdateDelete):
    version_num = models.IntegerField(db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(db_column='UpdatedOn', default=None)
    updated_by = models.TextField(db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(db_column='BaseVersion', default=None)
    comments = models.TextField(db_column='Comments', default=None)
    point_type_id = models.ForeignKey(PointType, db_column='PointTypeID', on_delete=models.CASCADE)
    point_type_version_id = models.BigAutoField(db_column='PointTypeVersionID', primary_key=True, serialize=False)
    point_type_name = models.TextField(db_column='PointTypeName', max_length=4000, null=False, default=None)
    point_type_order_id = models.IntegerField(db_column='PointTypeOrderID', null=False, default=None)

    def __str__(self):
        return str(self.point_type_version_id)

    class Meta:
        index_together = (("point_type_id", "version_num"))
        verbose_name_plural = 'PointType_History'
        db_table = 'PointType_History'


class ServiceType(Delete):
    service_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceTypeID")
    service_class = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceClass")
    service_type_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceTypeName")
    service_type_description = models.TextField(
        max_length=50, null=False, blank=False, db_column="ServiceTypeDescription")

    def __str__(self):
        return str(self.service_type_id)

    class Meta:
        verbose_name_plural = 'ServiceType'
        db_table = "ServiceType"


class ServiceTypeHistory(CommentUpdateDelete):
    service_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceTypeVersionID")
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, db_column="ServiceTypeID")
    service_class = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceClass")
    service_type_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceTypeName")
    service_type_description = models.TextField(
        max_length=50, null=False, blank=False, db_column="ServiceTypeDescription")

    def __str__(self):
        return str(self.service_type_version_id)

    class Meta:
        index_together = (('service_type', 'version_num'))
        verbose_name_plural = 'ServiceType_History'
        db_table = "ServiceType_History"


class AccessorialDetail(Delete):
    acc_detail_id = models.BigAutoField(
        db_column='AccDetailID', primary_key=True, serialize=False)
    tmacc_detail_id = models.TextField(
        db_column='TMAccDetailID',max_length=40, null=True, default=None)
    allow_between = models.BooleanField(
        db_column='AllowBetween', default=False)
    carrier_movement_type = models.TextField(
        db_column='CarrierMovementType', max_length=1, null=True, default=None)
    acc_rate_custom_maximum = models.DecimalField(
        db_column='AccRateCustomMaximum', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_custom_minimum = models.DecimalField(
        db_column='AccRateCustomMinimum', decimal_places=6, max_digits=19, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', null=True, default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    acc_rate_dock = models.BooleanField(
        db_column='AccRateDock', default=False)
    acc_rate_DOE_factorA = models.DecimalField(
        db_column='AccRateDOEFactorA', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_DOE_factorB = models.DecimalField(
        db_column='AccRateDOEFactorB', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_elevator = models.BooleanField(
        db_column='AccRateElevator', default=False)
    acc_rate_exclude_legs = models.BooleanField(
        db_column='AccRateExcludeLegs', default=False)
    acc_rate_extra_stop_rates = models.TextField(
        db_column='AccRateExtraStopRates', max_length=4000, null=True, default=None)
    acc_rate_increment = models.DecimalField(
        db_column='AccRateIncrement', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_fuel_price_average = models.TextField(
        db_column='AccRateFuelPriceAverage', max_length=10, null=True, default=None)
    acc_rate_max_charge = models.DecimalField(
        db_column='AccRateMaxCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_min_charge = models.DecimalField(
        db_column='AccRateMinCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_percent = models.DecimalField(
        db_column='AccRatePercent', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_shipping_instructionID = models.BigIntegerField(
        db_column='AccRateShippingInstructionID', default=None, null=True)
    acc_rate_survey = models.BooleanField(
        db_column='AccRateSurvey', default=False)
    acc_rate_stairs = models.BooleanField(
        db_column='AccRateStairs', default=False)
    acc_rate_status_code = models.TextField(
        db_column='AccRateStatusCode', max_length=10, null=True, default=None)
    acc_rate_threshold_amount = models.DecimalField(
        db_column='AccRateThresholdAmount', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_vehicle_restricted = models.BooleanField(
        db_column='AccRateVehicleRestricted', default=False)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')
    acc_rate_factor = models.DecimalField(
        db_column='AccRateFactor', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1ID = models.ForeignKey(
        AccRangeType, db_column='AccRateRangeField1ID', on_delete=models.CASCADE, related_name='+', null=True)
    commodity_id = models.ForeignKey(
        Commodity, db_column='CommodityID', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, related_name='+', null=True,
        blank=True)
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="OriginTypeID", related_name="+")
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="DestinationTypeID", related_name="+")
    acc_rate_range_field2ID = models.DecimalField(
        db_column='AccRateRangeField2ID', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1_to = models.DecimalField(
        db_column='AccRateRangeField1To', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1_from = models.DecimalField(
        db_column='AccRateRangeField1From', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field2_to = models.DecimalField(
        db_column='AccRateRangeField2To', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field2_from = models.DecimalField(
        db_column='AccRateRangeField2From', decimal_places=6, max_digits=19, null=True, default=None)
    acc_min = models.DecimalField(
        db_column='AccMin', decimal_places=6, max_digits=19, null=True, default=None)
    acc_max = models.DecimalField(
        db_column='AccMax', decimal_places=6, max_digits=19, null=True, default=None)
    acc_percent = models.DecimalField(
        db_column='AccPercent', decimal_places=6, max_digits=19, null=True, default=None)
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, null=True, db_column="ServiceTypeID")

    def __str__(self):
        return str(self.acc_detail_id)

    class Meta:
        verbose_name_plural = 'AccessorialDetail'
        db_table = 'AccessorialDetail'


class AccessorialDetailHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_detail_version_id = models.BigAutoField(
        db_column='AccDetailVersionID', primary_key=True, serialize=False)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    tmacc_detail_id = models.TextField(
        db_column='TMAccDetailID', max_length=40, null=True, default=None)
    allow_between = models.BooleanField(
        db_column='AllowBetween', default=False)
    carrier_movement_type = models.TextField(
        db_column='CarrierMovementType', max_length=1, null=True, default=None)
    acc_rate_custom_maximum = models.DecimalField(
        db_column='AccRateCustomMaximum', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_custom_minimum = models.DecimalField(
        db_column='AccRateCustomMinimum', decimal_places=6, max_digits=19, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', null=True, default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', null=True, default=None)
    acc_rate_dock = models.BooleanField(
        db_column='AccRateDock', default=False)
    acc_rate_DOE_factorA = models.DecimalField(
        db_column='AccRateDOEFactorA', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_DOE_factorB = models.DecimalField(
        db_column='AccRateDOEFactorB', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_elevator = models.BooleanField(
        db_column='AccRateElevator', default=False)
    acc_rate_exclude_legs = models.BooleanField(
        db_column='AccRateExcludeLegs', default=False)
    acc_rate_extra_stop_rates = models.TextField(
        db_column='AccRateExtraStopRates', max_length=4000, null=True, default=None)
    acc_rate_increment = models.DecimalField(
        db_column='AccRateIncrement', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_fuel_price_average = models.TextField(
        db_column='AccRateFuelPriceAverage', max_length=10, null=True, default=None)
    acc_rate_max_charge = models.DecimalField(
        db_column='AccRateMaxCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_min_charge = models.DecimalField(
        db_column='AccRateMinCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_percent = models.DecimalField(
        db_column='AccRatePercent', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1_version_id = models.BigIntegerField(
        db_column='AccRateRangeField1VersionID', default=None, null=True)
    acc_rate_range_field2_version_id = models.BigIntegerField(
        db_column='AccRateRangeField2VersionID', default=None, null=True)
    acc_rate_shipping_instructionID = models.BigIntegerField(db_column='AccRateShippingInstructionID', default=None,
                                                             null=True)
    acc_rate_survey = models.BooleanField(
        db_column='AccRateSurvey', default=False)
    acc_rate_stairs = models.BooleanField(
        db_column='AccRateStairs', default=False)
    acc_rate_status_code = models.TextField(
        db_column='AccRateStatusCode', max_length=10, null=True, default=None)
    acc_rate_threshold_amount = models.DecimalField(
        db_column='AccRateThresholdAmount', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_vehicle_restricted = models.BooleanField(
        db_column='AccRateVehicleRestricted', default=False)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_factor = models.DecimalField(
        db_column='AccRateFactor', decimal_places=6, max_digits=19, null=True, default=None)
    acc_range_type_version_id = models.ForeignKey(
        AccRangeTypeHistory, db_column='AccRangeTypeVersionID', null=True, on_delete=models.CASCADE, related_name='+')
    commodity_version_id = models.ForeignKey(
        CommodityHistory, db_column='CommodityVersionID', null=True, on_delete=models.CASCADE, related_name='+')
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE, related_name='+', null=True)
    acc_detail_id = models.ForeignKey(
        AccessorialDetail, db_column='AccDetailID', on_delete=models.CASCADE, related_name='+')
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="OriginTypeVersionID",
        related_name="+")
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTypeVersionID",
        related_name="+")
    acc_rate_range_field2ID = models.DecimalField(
        db_column='AccRateRangeField2ID', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1_to = models.DecimalField(
        db_column='AccRateRangeField1To', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1_from = models.DecimalField(
        db_column='AccRateRangeField1From', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field2_to = models.DecimalField(
        db_column='AccRateRangeField2To', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field2_from = models.DecimalField(
        db_column='AccRateRangeField2From', decimal_places=6, max_digits=19, null=True, default=None)
    acc_min = models.DecimalField(
        db_column='AccMin', decimal_places=6, max_digits=19, null=True, default=None)
    acc_max = models.DecimalField(
        db_column='AccMax', decimal_places=6, max_digits=19, null=True, default=None)
    acc_percent = models.DecimalField(
        db_column='AccPercent', decimal_places=6, max_digits=19, null=True, default=None)
    service_type_version = models.ForeignKey(
        ServiceTypeHistory, on_delete=models.CASCADE, null=True, db_column="ServiceTypeVersionID")

    def __str__(self):
        return str(self.acc_detail_version_id)

    class Meta:
        index_together = (("acc_detail_id", "version_num"))
        verbose_name_plural = 'AccessorialDetail_History'
        db_table = 'AccessorialDetail_History'


class AccessorialDetention(Delete):
    acc_detention_id = models.BigAutoField(
        db_column='AccDetentionID', primary_key=True, serialize=False)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')
    tm_detention_id = models.BigIntegerField(
        db_column='TMDetentionID', default=None)
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    detention_type = models.CharField(
        db_column='DetentionType', max_length=50, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    exclude_closed_days_detention = models.TextField(
        db_column='ExcludeClosedDaysDetention', max_length=20, null=True, default=None)
    exclude_closed_days_freetime = models.TextField(
        db_column='ExcludeClosedDaysFreeTime', max_length=20, null=True, default=None)
    fb_based_date_field = models.TextField(
        db_column='FBBasedDateField', max_length=10, null=True, default=None)
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=3, null=True, default=None)
    freetime_unit_to_measure = models.TextField(
        db_column='FreeTimeUnitofMeasure', max_length=10, null=True, default=None)
    inter_company = models.TextField(
        db_column='InterCompany', max_length=5, null=True, default=None)
    late_no_bill = models.TextField(
        db_column='LateNoBill', max_length=5, null=True, default=None)
    late_window = models.DecimalField(
        db_column='LateWindow', decimal_places=6, max_digits=19, null=True, default=None)
    ltl_proration_method = models.TextField(
        db_column='LtlProrationMethod', max_length=10, null=True, default=None)
    max_bill_time = models.DecimalField(
        db_column='MaxBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_bill_time = models.DecimalField(
        db_column='MinBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    free_times = models.TextField(
        db_column='FreeTimes', max_length=4000, null=True, default=None)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    payment_option = models.TextField(
        db_column='PaymentOption', max_length=10, null=True, default=None)
    second_bill_rate = models.DecimalField(
        db_column='SecondBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    shipper = models.TextField(
        db_column='Shipper', max_length=10, null=True, default=None)
    shipper_group = models.TextField(
        db_column='ShipperGroup', max_length=10, null=True, default=None)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    destination_type = models.TextField(
        db_column='DestinationType', max_length=40, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    start_bill_rate = models.DecimalField(
        db_column='StartBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    start_option = models.TextField(
        db_column='StartOption', max_length=40, null=True, default=None)
    stop_option = models.TextField(
        db_column='StopOption', max_length=40, null=True, default=None)
    use_actual_time = models.BooleanField(
        db_column='UseActualTime', default=False)
    warning_send = models.TextField(
        db_column='WarningSend', max_length=5, null=True, default=None)
    warning_time = models.DecimalField(
        db_column='WarningTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    currency_id = models.ForeignKey(
        Currency, db_column='CurrencyID', on_delete=models.CASCADE, related_name='+')
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, null=True, related_name='+')
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="OriginTypeID", related_name="+")
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="DestinationTypeID", related_name="+")
    rate_unit = models.TextField(
        db_column='RateUnit', max_length=10, null=True, default=None)
    calc_order = models.BigIntegerField(
        db_column='CalcOrder', null=True, default=None)

    def __str__(self):
        return str(self.acc_detention_id)

    class Meta:
        verbose_name_plural = 'AccessorialDetention'
        db_table = 'AccessorialDetention'


class AccessorialDetentionHistory(Delete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_detention_version_id = models.BigAutoField(
        db_column='AccDetentionVersionID', primary_key=True, serialize=False)
    tm_detention_id = models.BigIntegerField(
        db_column='TMDetentionID', default=None)
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    detention_type = models.CharField(
        db_column='DetentionType', max_length=50, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    exclude_closed_days_detention = models.TextField(
        db_column='ExcludeClosedDaysDetention', max_length=20, null=True, default=None)
    exclude_closed_days_freetime = models.TextField(
        db_column='ExcludeClosedDaysFreeTime', max_length=20, null=True, default=None)
    fb_based_date_field = models.TextField(
        db_column='FBBasedDateField', max_length=10, null=True, default=None)
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=3, null=True, default=None)
    freetime_unit_to_measure = models.TextField(
        db_column='FreeTimeUnitofMeasure', max_length=10, null=True, default=None)
    inter_company = models.TextField(
        db_column='InterCompany', max_length=5, null=True, default=None)
    late_no_bill = models.TextField(
        db_column='LateNoBill', max_length=5, null=True, default=None)
    late_window = models.DecimalField(
        db_column='LateWindow', decimal_places=6, max_digits=19, null=True, default=None)
    ltl_proration_method = models.TextField(
        db_column='LtlProrationMethod', max_length=10, null=True, default=None)
    max_bill_time = models.DecimalField(
        db_column='MaxBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_bill_time = models.DecimalField(
        db_column='MinBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    free_times = models.TextField(
        db_column='FreeTimes', max_length=4000, null=True, default=None)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    payment_option = models.TextField(
        db_column='PaymentOption', max_length=10, null=True, default=None)
    second_bill_rate = models.DecimalField(
        db_column='SecondBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    shipper = models.TextField(
        db_column='Shipper', max_length=10, null=True, default=None)
    shipper_group = models.TextField(
        db_column='ShipperGroup', max_length=10, null=True, default=None)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    destination_type = models.TextField(
        db_column='DestinationType', max_length=40, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    start_bill_rate = models.DecimalField(
        db_column='StartBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    start_option = models.TextField(
        db_column='StartOption', max_length=40, null=True, default=None)
    stop_option = models.TextField(
        db_column='StopOption', max_length=40, null=True, default=None)
    use_actual_time = models.BooleanField(
        db_column='UseActualTime', default=False)
    warning_send = models.TextField(
        db_column='WarningSend', max_length=5, null=True, default=None)
    warning_time = models.DecimalField(
        db_column='WarningTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    currency_version_id = models.ForeignKey(
        CurrencyHistory, db_column='CurrencyVersionID', on_delete=models.CASCADE, related_name='+')
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID',  null=True, on_delete=models.CASCADE)
    acc_detention_id = models.ForeignKey(
        AccessorialDetention, db_column='AccDetentionID', on_delete=models.CASCADE)
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="OriginTypeVersionID",
        related_name="+")
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTypeVersionID",
        related_name="+")
    rate_unit = models.TextField(
        db_column='RateUnit', max_length=10, null=True, default=None)
    calc_order = models.BigIntegerField(
        db_column='CalcOrder', null=True, default=None)

    def __str__(self):
        return str(self.acc_detention_version_id)

    class Meta:
        index_together = (("acc_detention_id", "version_num"))
        verbose_name_plural = 'AccessorialDetention_History'
        db_table = 'AccessorialDetention_History'


class AccessorialStorage(Delete):
    acc_storage_id = models.BigAutoField(
        db_column='AccStorageID', primary_key=True, serialize=False)
    tm_storage_id = models.BigIntegerField(
        db_column='TMStorageID', default=None)
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    bill_option = models.TextField(
        db_column='BillOption', max_length=1, null=True, default=None)
    dangerous_goods = models.BooleanField(
        db_column='DangerousGoods', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    free_days = models.BigIntegerField(
        db_column='FreeDays', default=None)
    high_value = models.BooleanField(
        db_column='HighValue', default=False)
    include_delivery_day = models.BooleanField(
        db_column='IncludeDeliveryDay', default=False)
    include_terminal_service_calendar = models.BooleanField(
        db_column='IncludeTerminalServiceCalendar', default=False)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    rate_amount = models.DecimalField(
        db_column='RateAmount', decimal_places=6, max_digits=19, null=True, default=None)
    rate_max = models.DecimalField(
        db_column='RateMax', decimal_places=6, max_digits=19, null=True, default=None)
    rate_min = models.DecimalField(
        db_column='RateMin', decimal_places=6, max_digits=19, null=True, default=None)
    rate_per = models.DecimalField(
        db_column='RatePer', decimal_places=6, max_digits=19, null=True, default=None)
    temp_controlled = models.BooleanField(
        db_column='TempControlled', default=False)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE)
    currency_id = models.ForeignKey(
        Currency, db_column='CurrencyID', on_delete=models.CASCADE, related_name='+')
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, null=True)
    unit_id = models.ForeignKey(
        Unit, db_column='UnitID', on_delete=models.CASCADE, related_name='+')
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    calc_order = models.BigIntegerField(
        db_column='CalcOrder', null=True, default=None)

    def __str__(self):
        return str(self.acc_storage_id)

    class Meta:
        verbose_name_plural = 'AccessorialStorage'
        db_table = 'AccessorialStorage'


class AccessorialStorageHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_storage_id = models.ForeignKey(
        AccessorialStorage, db_column='AccStorageID', on_delete=models.CASCADE)
    acc_storage_version_id = models.BigAutoField(
        db_column='AccStorageVersionID', primary_key=True, serialize=False)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    tm_storage_id = models.BigIntegerField(
        db_column='TMStorageID', default=None)
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    bill_option = models.TextField(
        db_column='BillOption', max_length=1, null=True, default=None)
    dangerous_goods = models.BooleanField(
        db_column='DangerousGoods', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    free_days = models.BigIntegerField(
        db_column='FreeDays', default=None)
    high_value = models.BooleanField(
        db_column='HighValue', default=False)
    include_delivery_day = models.BooleanField(
        db_column='IncludeDeliveryDay', default=False)
    include_terminal_service_calendar = models.BooleanField(
        db_column='IncludeTerminalServiceCalendar', default=False)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    rate_amount = models.DecimalField(
        db_column='RateAmount', decimal_places=6, max_digits=19, null=True, default=None)
    rate_max = models.DecimalField(
        db_column='RateMax', decimal_places=6, max_digits=19, null=True, default=None)
    rate_min = models.DecimalField(
        db_column='RateMin', decimal_places=6, max_digits=19, null=True, default=None)
    rate_per = models.DecimalField(db_column='RatePer', decimal_places=6, max_digits=19, null=True, default=None)
    temp_controlled = models.BooleanField(
        db_column='TempControlled', default=False)
    currency_version_id = models.ForeignKey(
        CurrencyHistory, db_column='CurrencyVersionID', on_delete=models.CASCADE, related_name='+')
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE, null=True)
    unit_version_id = models.ForeignKey(
        UnitHistory, db_column='UnitVersionID', on_delete=models.CASCADE, related_name='+')
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    calc_order = models.BigIntegerField(
        db_column='CalcOrder', null=True, default=None)

    def __str__(self):
        return str(self.acc_storage_version_id)

    class Meta:
        index_together = (("acc_storage_id", "version_num"))
        verbose_name_plural = 'AccessorialStorage_History'
        db_table = 'AccessorialStorage_History'


class CustomerZones(Delete):
    customer_zone_id = models.BigAutoField(
        max_length=8, primary_key=True, null=False, db_column="CustomerZoneID")
    customer_zone_name = models.TextField(
        max_length=40, null=True, blank=False, db_column="CustomerZoneName")
    customer_zone_external_tmid = models.TextField(
        max_length=50, null=True, blank=False, db_column="ExternalTMID")
    customer_zone_code = models.TextField(
        max_length=10, null=True, blank=False, db_column="CustomerZoneCode")

    def __str__(self):
        return str(self.customer_zone_id)

    class Meta:
        verbose_name_plural = 'CustomerZones'
        db_table = 'CustomerZones'


class CustomerZonesHistory(Delete):
    version_num = models.IntegerField(
        default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
        default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
        default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
        default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
        default=False, null=False, db_column="Comments")
    customer_zone_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CustomerZoneVersionID")
    customer_zone_id = models.ForeignKey(
        CustomerZones, on_delete=models.CASCADE, db_column="CustomerZoneID", related_name="+")
    customer_zone_name = models.TextField(
        max_length=40, null=True, blank=False, db_column="CustomerZoneName")
    customer_zone_external_tmid = models.TextField(
        max_length=50, null=True, blank=False, db_column="ExternalTMID")
    customer_zone_code = models.TextField(
        max_length=10, null=True, blank=False, db_column="CustomerZoneCode")

    def __str__(self):
        return str(self.customer_zone_version_id)

    class Meta:
        index_together = (("customer_zone_id", "version_num"))
        verbose_name_plural = 'CustomerZones_History'
        db_table = 'CustomerZones_History'


class SubPostalCode(Delete):
    sub_postal_code_id = models.BigAutoField(
        max_length=8, primary_key=True, null=False, db_column="SubPostalCodeID")
    sub_postal_code_name = models.TextField(
        max_length=40, null=True, blank=False, db_column="SubPostalCodeName")
    terminal_id = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, db_column="TerminalID")

    def __str__(self):
        return str(self.sub_postal_code_id)

    class Meta:
        verbose_name_plural = 'SubPostalCode'
        db_table = 'SubPostalCode'


class SubPostalCodeHistory(Delete):
    version_num = models.IntegerField(
        default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
        default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
        default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
        default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
        default=False, null=False, db_column="Comments")
    sub_postal_code_version_id = models.BigAutoField(
        max_length=8, primary_key=True, null=False, db_column="SubPostalCodeVersionID")
    sub_postal_code_id = models.ForeignKey(
        SubPostalCode, on_delete=models.CASCADE, db_column="SubPostalCodeID")
    sub_postal_code_name = models.TextField(
        max_length=40, null=True, blank=False, db_column="SubPostalCodeName")
    terminal_version_id = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, null=True, db_column="TerminalVersionID")

    def __str__(self):
        return str(self.sub_postal_code_version_id)

    class Meta:
        index_together = (("sub_postal_code_id", "version_num"))
        verbose_name_plural = 'SubPostalCode_History'
        db_table = 'SubPostalCode_History'


class RequestSection(Delete):
    request_section_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionID")
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    rate_base = models.ForeignKey(
        RateBase, null=True, on_delete=models.CASCADE, db_column="RateBaseID")
    override_class = models.ForeignKey(
        FreightClass, null=True, on_delete=models.CASCADE, db_column="OverrideClassID")
    equipment_type = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeID", related_name="+")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    weight_break_header = models.ForeignKey(
        WeightBreakHeader, on_delete=models.CASCADE, db_column="WeightBreakHeaderID", null=True)
    section_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="SectionName")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    commodity_id = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, null=True, blank=True, default=None, db_column="CommodityID")
    unit_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, default=100, db_column="UnitFactor")
    maximum_value = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, default=100, db_column="MaximumValue")
    as_rating = models.BooleanField(
        null=False, default=True, db_column="AsRating")
    has_min = models.BooleanField(
        null=False, default=True, db_column="HasMin")
    has_max = models.BooleanField(
        null=False, default=True, db_column="HasMax")
    base_rate = models.BooleanField(
        null=False, default=True, db_column="BaseRate")
    request_section_source_id = models.BigIntegerField(null=True, blank=True, default=None,
                                                       db_column="RequestSectionSourceID")
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.request_section_id)

    class Meta:
        verbose_name_plural = 'RequestSection'
        db_table = 'RequestSection'


class RequestSectionHistory(CommentUpdateDelete):
    request_section_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionVersionID")
    request_section = models.ForeignKey(
        RequestSection, on_delete=models.CASCADE, db_column="RequestSectionID")
    request_version_id = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, db_column="RequestVersionID")
    sub_service_level_version = models.ForeignKey(
        SubServiceLevelHistory, on_delete=models.CASCADE, db_column="SubServiceLevelVersionID")
    rate_base_version = models.ForeignKey(
        RateBaseHistory, null=True, on_delete=models.CASCADE, db_column="RateBaseVersionID")
    override_class_version = models.ForeignKey(
        FreightClassHistory, null=True, on_delete=models.CASCADE, db_column="OverrideClassVersionID")
    equipment_type_version = models.ForeignKey(
        EquipmentTypeHistory, null=True, on_delete=models.CASCADE, db_column="EquipmentTypeVersionID")
    weight_break_header_version = models.ForeignKey(
        WeightBreakHeaderHistory, on_delete=models.CASCADE, db_column="WeightBreakHeaderVersionID")
    section_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="SectionName")
    commodity_id = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, null=True, db_column="CommodityVersionID")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    override_density = models.DecimalField(max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    unit_factor = models.DecimalField(max_digits=19, decimal_places=6, null=True, db_column="UnitFactor")
    maximum_value = models.DecimalField(max_digits=19, decimal_places=6, null=True, db_column="MaximumValue")
    as_rating = models.BooleanField(null=True, db_column="AsRating")
    has_min = models.BooleanField(null=True, db_column="HasMin")
    has_max = models.BooleanField(null=True, db_column="HasMax")
    base_rate = models.BooleanField(null=True, db_column="BaseRate")
    request_section_source_id = models.BigIntegerField(null=True, blank=True, default=None,
                                                       db_column="RequestSectionSourceID")
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.request_section_version_id)

    class Meta:
        # TODO enable indices back when we're fix issues with Django <-> SQL indices
        index_together = (('request_section', 'version_num'))
        verbose_name_plural = 'RequestSection_History'
        db_table = 'RequestSection_History'


class RequestSectionLanePointType(Delete):
    request_section_lane_point_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePointTypeID")
    request_section_lane_point_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestSectionLanePointTypeName")
    service_offering = models.ForeignKey(
        ServiceOffering, null=False, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    location_hierarchy = models.IntegerField(
        null=False, blank=False, db_column="LocationHierarchy")
    is_group_type = models.BooleanField(
        null=False, default=False, db_column="IsGroupType")
    is_point_type = models.BooleanField(
        null=False, default=False, db_column="IsPointType")

    def __str__(self):
        return str(self.request_section_lane_point_type_id)

    class Meta:
        verbose_name_plural = 'RequestSectionLanePointType'
        db_table = 'RequestSectionLanePointType'


class RequestSectionLanePointTypeHistory(CommentUpdateDelete):
    request_section_lane_point_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePointTypeVersionID")
    request_section_lane_point_type = models.ForeignKey(
        RequestSectionLanePointType, null=False, on_delete=models.CASCADE, db_column="RequestSectionLanePointTypeID")
    request_section_lane_point_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestSectionLanePointTypeName")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, null=False, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    location_hierarchy = models.IntegerField(
        null=False, blank=False, db_column="LocationHierarchy")
    is_group_type = models.BooleanField(
        null=False, default=False, db_column="IsGroupType")
    is_point_type = models.BooleanField(
        null=False, default=False, db_column="IsPointType")

    def __str__(self):
        return str(self.request_section_lane_point_type_version_id)

    class Meta:
        index_together = (('request_section_lane_point_type', 'version_num'))
        verbose_name_plural = 'RequestSectionLanePointType_History'
        db_table = 'RequestSectionLanePointType_History'


class RequestSectionLane(Delete):
    request_section_lane_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLaneID")
    request_section = models.ForeignKey(
        RequestSection, on_delete=models.CASCADE, db_column="RequestSectionID")
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=False, default=1, db_column="OriginTypeID", related_name="+")
    origin_id = models.BigIntegerField(null=False, default=1, db_column="OriginID")
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=False, default=1, db_column="DestinationTypeID", related_name="+")
    destination_id = models.BigIntegerField(null=False, default=1, db_column="DestinationID")
    is_published = models.BooleanField(
        null=False, default=False, db_column="IsPublished")
    is_edited = models.BooleanField(
        null=False, default=False, db_column="IsEdited")
    is_duplicate = models.BooleanField(
        null=False, default=False, db_column="IsDuplicate")
    is_between = models.BooleanField(
        null=False, default=False, db_column="IsBetween")
    commitment = models.TextField(
        blank=False, default="[]", db_column="Commitment")
    customer_rate = models.TextField(
        blank=False, default="[]", db_column="CustomerRate")
    customer_discount = models.TextField(
        blank=False, default="[]", db_column="CustomerDiscount")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    partner_rate = models.TextField(
        blank=False, default="[]", db_column="PartnerRate")
    partner_discount = models.TextField(
        blank=False, default="[]", db_column="PartnerDiscount")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="DoNotMeetCommitment")
    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_excluded = models.BooleanField(
        null=True, default=False, db_column="IsExcluded")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")
    request_section_lane_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSectionLaneSourceID")
    deficit = models.TextField(
        db_column='Deficit', max_length=4000, null=True, default=None)
    impact_percentage = models.TextField(
        db_column='ImpactPercentage', max_length=4000, null=True, default=None)
    embedded_cost = models.TextField(
        db_column='EmbeddedCost', max_length=4000, null=True, default=None)
    cost = models.TextField(blank=False, default="[]", db_column="Cost")
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.request_section_lane_id)

    class Meta:
        verbose_name_plural = 'RequestSectionLane'
        db_table = 'RequestSectionLane'


class RequestSectionLaneHistory(CommentUpdateDelete):
    request_section_lane_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLaneVersionID")
    request_section_lane = models.ForeignKey(
        RequestSectionLane, on_delete=models.CASCADE, db_column="RequestSectionLaneID")
    request_section_version = models.ForeignKey(
        RequestSectionHistory, on_delete=models.CASCADE, db_column="RequestSectionVersionID")
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="OriginTypeVersionID", related_name="+")
    origin_id = models.BigIntegerField(null=True, db_column="OriginID")
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTypeVersionID", related_name="+")
    destination_id = models.BigIntegerField(null=True, db_column="DestinationID")
    is_published = models.BooleanField(
        null=False, default=False, db_column="IsPublished")
    is_edited = models.BooleanField(
        null=False, default=False, db_column="IsEdited")
    is_duplicate = models.BooleanField(
        null=False, default=False, db_column="IsDuplicate")
    is_between = models.BooleanField(
        null=False, default=False, db_column="IsBetween")
    commitment = models.TextField(
        blank=False, default="[]", db_column="Commitment")
    customer_rate = models.TextField(
        blank=False, default="[]", db_column="CustomerRate")
    customer_discount = models.TextField(
        blank=False, default="[]", db_column="CustomerDiscount")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    partner_rate = models.TextField(
        blank=False, default="[]", db_column="PartnerRate")
    partner_discount = models.TextField(
        blank=False, default="[]", db_column="PartnerDiscount")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="DoNotMeetCommitment")
    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_excluded = models.BooleanField(
        null=True, default=False, db_column="IsExcluded")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")
    request_section_lane_source_id = models.ForeignKey(
        RequestSectionLane, on_delete=models.CASCADE, null=True, blank=False,
        db_column="RequestSectionLaneSourceID", related_name="+")
    deficit = models.TextField(
        db_column='Deficit', max_length=4000, null=True, default=None)
    impact_percentage = models.TextField(
        db_column='ImpactPercentage', max_length=4000, null=True, default=None)
    embedded_cost = models.TextField(
        db_column='EmbeddedCost', max_length=4000, null=True, default=None)

    request_section_lane_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSectionLaneSourceID")
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.request_section_lane_version_id)

    class Meta:
        index_together = (('request_section_lane', 'version_num'))
        verbose_name_plural = 'RequestSectionLane_History'
        db_table = 'RequestSectionLane_History'


class RequestSectionLanePricingPoint(Delete):
    request_section_lane_pricing_point_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePricingPointID")
    request_section_lane = models.ForeignKey(
        RequestSectionLane, on_delete=models.CASCADE, db_column="RequestSectionLaneID")
    origin_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=False, db_column="OriginPostalCodeID", related_name="+")
    destination_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=False, db_column="DestinationPostalCodeID", related_name="+")
    origin_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="OriginPostalCodeName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="DestinationPostalCodeName")
    pricing_point_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="PricingPointNumber")
    pricing_point_hash_code = models.BinaryField(null=False, db_column="PricingPointHashCode")
    cost = models.TextField(null=False, db_column="Cost")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    fak_rate = models.TextField(blank=False, default="[]", db_column="FakRate")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    splits_all = models.TextField(
        blank=False, default="[]", db_column="SplitsAll")
    splits_all_usage_percentage = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SplitsAllUsagePercentage")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    is_flagged = models.BooleanField(null=True, db_column="IsFlagged", default=False)

    # 1837
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(blank=True, null=True, default="[]",
                                                 db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(blank=True, null=True, default="[]",
                                                   db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")
    request_section_lane_pricing_point_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSectionLanePricingPointSourceID")

    def __str__(self):
        return str(self.request_section_lane_pricing_point_id)

    class Meta:
        verbose_name_plural = 'RequestSectionLanePricingPoint'
        db_table = 'RequestSectionLanePricingPoint'


class RequestSectionLanePricingPointHistory(CommentUpdateDelete):
    request_section_lane_pricing_point_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePricingPointVersionID")
    request_section_lane_pricing_point = models.ForeignKey(
        RequestSectionLanePricingPoint, on_delete=models.CASCADE, db_column="RequestSectionLanePricingPointID")
    request_section_lane_version = models.ForeignKey(
        RequestSectionLaneHistory, on_delete=models.CASCADE, db_column="RequestSectionLaneVersionID")
    origin_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=False, db_column="OriginPostalCodeVersionID",
        related_name="+")
    destination_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=False, db_column="DestinationPostalCodeVersionID",
        related_name="+")
    origin_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="OriginPostalCodeName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="DestinationPostalCodeName")
    pricing_point_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="PricingPointNumber")
    pricing_point_hash_code = models.BinaryField(null=False, db_column="PricingPointHashCode")
    cost = models.TextField(null=False, db_column="Cost")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    fak_rate = models.TextField(blank=False, default="[]", db_column="FakRate")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    splits_all = models.TextField(
        blank=False, default="[]", db_column="SplitsAll")
    splits_all_usage_percentage = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SplitsAllUsagePercentage")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")

    # 1837
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(blank=True, null=True, default="[]",
                                                 db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(blank=True, null=True, default="[]",
                                                   db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")
    request_section_lane_pricing_point_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="RequestSectionLanePricingPointSourceID")

    def __str__(self):
        return str(self.request_section_lane_pricing_point_version_id)

    class Meta:
        index_together = (
            ('request_section_lane_pricing_point', 'version_num'))
        verbose_name_plural = 'RequestSectionLanePricingPoint_History'
        db_table = 'RequestSectionLanePricingPoint_History'


class RequestProfile(Delete):
    request_profile_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestProfileID")
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    using_standard_tariff = models.BooleanField(
        null=True, default=False, db_column="UsingStandardTariff")
    exclude_from_fak_rating = models.BooleanField(
        null=True, default=False, db_column="ExcludeFromFAKRating")
    use_actual_weight = models.BooleanField(
        null=True, default=False, db_column="UseActualWeight")
    is_class_density = models.BooleanField(
        null=True, default=False, db_column="IsClassDensity")
    avg_weight_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedDensity")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    subject_to_cube = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SubjectToCube")
    linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="LinearLengthRule")
    weight_per_linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="WeightPerLinearLengthRule")
    avg_weighted_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedClass")
    override_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideClass")
    freight_elements = models.TextField(
        null=True, blank=False, default="[]", db_column="FreightElements")
    shipments = models.TextField(
        null=True, blank=False, default="[]", db_column="Shipments")
    shipping_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ShippingControls")
    competitors = models.TextField(
        null=True, blank=False, default="[]", db_column="Competitors")
    class_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ClassControls")

    def __str__(self):
        return str(self.request_profile_id)

    class Meta:
        verbose_name_plural = 'RequestProfile'
        db_table = 'RequestProfile'


class RequestProfileHistory(CommentUpdateDelete):
    request_profile_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestProfileVersionID")
    request_profile = models.ForeignKey(
        RequestProfile, on_delete=models.CASCADE, db_column="RequestProfileID")
    request_id = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, db_column="RequestVersionID")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    using_standard_tariff = models.BooleanField(
        null=True, default=False, db_column="UsingStandardTariff")
    exclude_from_fak_rating = models.BooleanField(
        null=True, default=False, db_column="ExcludeFromFAKRating")
    use_actual_weight = models.BooleanField(
        null=True, default=False, db_column="UseActualWeight")
    is_class_density = models.BooleanField(
        null=True, default=False, db_column="IsClassDensity")
    avg_weight_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedDensity")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    subject_to_cube = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SubjectToCube")
    linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="LinearLengthRule")
    weight_per_linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="WeightPerLinearLengthRule")
    avg_weighted_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedClass")
    override_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideClass")
    freight_elements = models.TextField(
        null=True, blank=False, default="[]", db_column="FreightElements")
    shipments = models.TextField(
        null=True, blank=False, default="[]", db_column="Shipments")
    shipping_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ShippingControls")
    competitors = models.TextField(
        null=True, blank=False, default="[]", db_column="Competitors")
    class_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ClassControls")

    def __str__(self):
        return str(self.request_profile_version_id)

    class Meta:
        index_together = (('request_profile', 'version_num'))
        verbose_name_plural = 'RequestProfile_History'
        db_table = 'RequestProfile_History'


class ServiceMatrix(Delete):
    service_matrix_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceMatrixID")
    service_type_id = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, null=True, db_column="ServiceTypeID")
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelID")
    point_id = models.IntegerField(
        null=True, db_column="PointID")
    point_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, db_column="PointTypeID")

    def __str__(self):
        return str(self.service_matrix_id)

    class Meta:
        verbose_name_plural = 'ServiceMatrix'
        db_table = "ServiceMatrix"


class ServiceMatrixHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
        default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
        default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
        default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
        default=False, null=False, db_column="Comments")
    service_matrix_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceMatrixVersionID")
    service_matrix = models.ForeignKey(
        ServiceMatrix, on_delete=models.CASCADE, null=False, db_column="ServiceMatrixID")
    service_type_version_id = models.ForeignKey(
        ServiceTypeHistory, on_delete=models.CASCADE, null=True, db_column="ServiceTypeVersionID")
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelVersionID")
    point_version_id = models.IntegerField(
        null=True, db_column="PointVersionID")
    point_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="PointTypeVersionID")

    def __str__(self):
        return str(self.service_matrix_version_id)

    class Meta:
        index_together = (("service_matrix", "version_num"))
        verbose_name_plural = 'ServiceMatrix_History'
        db_table = "ServiceMatrix_History"


class LastAssignedUser(Delete):
    last_assigned_user_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LastAssignedUserID")
    persona_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="PersonaName")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=False, db_column="ServiceLevelID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")

    def __str__(self):
        return str(self.last_assigned_user_id)

    class Meta:
        unique_together = (('persona_name', 'service_level'))
        verbose_name_plural = 'LastAssignedUser'
        db_table = 'LastAssignedUser'


class UserServiceLevel(Delete):
    user_service_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserServiceLevelID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=False, db_column="ServiceLevelID")

    def __str__(self):
        return str(self.user_service_level_id)

    class Meta:
        verbose_name_plural = 'UserServiceLevel'
        db_table = 'UserServiceLevel'


class UserServiceLevelHistory(CommentUpdateDelete):
    user_service_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserServiceLevelVersionID")
    user_service_level = models.ForeignKey(
        UserServiceLevel, on_delete=models.CASCADE, null=False, db_column="UserServiceLevelID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=False, db_column="UserVersionID")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, null=False, db_column="ServiceLevelVersionID")

    def __str__(self):
        return str(self.user_service_level_version_id)

    class Meta:
        index_together = (('user_service_level', 'version_num'))
        verbose_name_plural = 'UserServiceLevel_History'
        db_table = 'UserServiceLevel_History'


class Tariff(Delete):
    tariff_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TariffID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    revision_number = models.IntegerField(null=False, default=1, db_column="RevisionNumber")
    tariff_number = models.TextField(null=False, max_length=30, default="_", db_column="TariffNumber")
    published_on = models.DateTimeField(
        auto_now_add=True, null=True, db_column="PublishedOn")
    expires_on = models.DateTimeField(
        auto_now_add=True, null=True, db_column="ExpiresOn")
    document_url = models.TextField(
        null=True, blank=False, db_column="DocumentUrl")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.tariff_id)

    class Meta:
        verbose_name_plural = 'Tariff'
        index_together = (('tariff_id', 'revision_number'))
        db_table = 'Tariff'


class TariffHistory(CommentUpdateDelete):
    tariff_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TariffVersionID")
    tariff = models.ForeignKey(
        Tariff, on_delete=models.CASCADE, null=False, db_column="TariffID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, null=False, db_column="RequestVersionID")
    revision_number = models.IntegerField(null=False, default=1, db_column="RevisionNumber")
    tariff_number = models.TextField(null=False, max_length=30, default="_", db_column="TariffNumber")
    published_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PublishedOn")
    expires_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="ExpiresOn")
    document_url = models.TextField(
        null=True, blank=False, db_column="DocumentUrl")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.tariff_version_id)

    class Meta:
        index_together = (('tariff', 'version_num'))
        verbose_name_plural = 'Tariff_History'
        db_table = 'Tariff_History'


class RequestEditorRight(Delete):
    request_editor_right_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestEditorRightID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="UserID")
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, db_column="NotificationID")

    def __str__(self):
        return str(self.request_editor_right_id)

    class Meta:
        verbose_name_plural = 'RequestEditorRight'
        db_table = 'RequestEditorRight'


class ImportFile(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    file_name = models.TextField(
        null=False, blank=False, db_column="FileName")
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    record_count = models.IntegerField(
        null=False, blank=False, db_column="RecordCount")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(default='UNDEFINED', null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    rate_type = models.TextField(default='UNDEFINED', null=False, blank=False, db_column="RateType")
    duplicate_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="DuplicateLaneCount")
    directional_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="DirectionalLaneCount")
    between_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="BetweenLaneCount")
    flagged_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="FlaggedCount")
    unserviceable_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="UnserviceableCount")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'ImportFile'
        db_table = 'ImportFile'


class RequestSectionLaneImportQueue(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    section_name = models.TextField(
        null=True, blank=False, db_column="SectionName")
    request_section_lane_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLaneID")

    orig_group_type_id = models.TextField(
        RequestSectionLanePointType, null=True, db_column="OriginGroupTypeId")
    origin_group_type_name = models.TextField(
        null=True, blank=False, db_column="OriginGroupTypeName")

    origin_group_id = models.TextField(
        null=True, blank=False, db_column="OriginGroupId")
    origin_group_code = models.TextField(
        null=True, blank=False, db_column="OriginGroupCode")

    origin_point_type_id = models.TextField(
        null=True, blank=False, db_column="OriginPointTypeId")
    origin_point_type_name = models.TextField(
        null=True, blank=False, db_column="OriginPointTypeName")

    origin_point_id = models.TextField(
        null=True, blank=False, db_column="OriginPointId")
    origin_point_code = models.TextField(
        null=True, blank=False, db_column="OriginPointCode")

    destination_group_type_id = models.TextField(
        null=True, blank=False, db_column="DestinationGroupTypeId")
    destination_group_type_name = models.TextField(
        null=True, blank=False, db_column="DestinationGroupTypeName")

    destination_group_id = models.TextField(
        null=True, blank=False, db_column="DestinationGroupId")
    destination_group_code = models.TextField(
        null=True, blank=False, db_column="DestinationGroupCode")

    destination_point_type_id = models.TextField(
        null=True, blank=False, db_column="DestinationPointTypeId")
    destination_point_type_name = models.TextField(
        null=True, blank=False, db_column="DestinationPointTypeName")

    destination_point_id = models.TextField(
        null=True, blank=False, db_column="DestinationPointId")
    destination_point_code = models.TextField(
        null=True, blank=False, db_column="DestinationPointCode")

    is_between = models.TextField(
        null=True, blank=False, db_column="IsBetween")

    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    status_message = models.TextField(
        null=True, blank=False, db_column="StatusMessage")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    file = models.ForeignKey(ImportFile, related_name='ImportFile', on_delete=models.CASCADE, db_column="File")

    initial_rec_order = models.IntegerField(
        null=True, blank=False, db_column="InitialRecOrder")

    # + request_section_id = data.get("request_section_id")
    # + orig_group_type_id = data.get("orig_group_type_id")
    # + orig_group_id = data.get("orig_group_id")
    # orig_point_type_id = data.get("orig_point_type_id")
    # orig_point_id = data.get("orig_point_id")
    # dest_group_type_id = data.get("dest_group_type_id")
    # dest_group_id = data.get("dest_group_id")
    # dest_point_type_id = data.get("dest_point_type_id")
    # dest_point_id = data.get("dest_point_id")
    # is_between = data.get("is_between")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'RequestSectionLaneImportQueue'
        db_table = 'RequestSectionLaneImportQueue'


class RequestSectionLanePricingPointImportQueue(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    section_name = models.TextField(
        null=True, blank=False, db_column="SectionName")
    request_section_lane_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLaneID")
    origin_point_code = models.TextField(
        null=True, blank=False, db_column="OriginPointCode")
    destination_point_code = models.TextField(
        null=True, blank=False, db_column="DestinationPointCode")
    request_section_lane_pricing_point_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLanePricingPointID")
    origin_post_code_id = models.TextField(
        null=True, blank=False, db_column="OriginPostCodeID")
    origin_postal_code_name = models.TextField(
        null=True, blank=False, db_column="OriginPostalCodeName")
    destination_post_code_id = models.TextField(
        null=True, blank=False, db_column="DestinationPostCodeID")
    destination_postal_code_name = models.TextField(
        null=True, blank=False, db_column="DestinationPostalCodeName")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    status_message = models.TextField(
        null=True, blank=False, db_column="StatusMessage")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(
        default="UNDEFINED", null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    file = models.ForeignKey(ImportFile, related_name='PricingPointsImportFile', on_delete=models.CASCADE,
                             db_column="File")
    origin_postal_code_id = models.IntegerField(
        null=True, blank=False, db_column="OriginPostalCodeId")
    destination_postal_code_id = models.IntegerField(
        null=True, blank=False, db_column="DestinationPostalCodeId")
    initial_rec_order = models.IntegerField(
        null=True, blank=False, db_column="InitialRecOrder")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'RequestSectionLanePricingPointImportQueue'
        db_table = 'RequestSectionLanePricingPointImportQueue'


class RequestEditorRightHistory(CommentUpdateDelete):
    request_editor_right_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestEditorRightVersionID")
    request_editor_right = models.ForeignKey(
        RequestEditorRight, on_delete=models.CASCADE, db_column="RequestEditorRightID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, db_column="RequestVersionID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, db_column="UserVersionID")
    notification_version = models.ForeignKey(
        NotificationHistory, on_delete=models.CASCADE, db_column="NotificationVersionID")

    def __str__(self):
        return str(self.request_editor_right_version_id)

    class Meta:
        verbose_name_plural = 'RequestEditorRight_History'
        db_table = 'RequestEditorRight_History'


class AccessorialOverride(Delete):
    acc_override_id = models.BigAutoField(
        db_column='AccOverrideID', primary_key=True, serialize=False)
    tmacc_override_id = models.BigIntegerField(
        db_column='TMAccOverrideID', default=1)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    allow_between = models.BooleanField(
        db_column='AllowBetween', default=False)
    carrier_movement_type = models.TextField(
        db_column='CarrierMovementType', max_length=1, null=True, default=None)
    commodity_id = models.ForeignKey(
        Commodity, db_column='CommodityID', on_delete=models.CASCADE, related_name='+', null=True, default=1)
    acc_rate_custom_maximum = models.DecimalField(
        db_column='AccRateCustomMaximum', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_custom_minimum = models.DecimalField(
        db_column='AccRateCustomMinimum', decimal_places=6, max_digits=19, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', null=True, default=datetime.now)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', null=True, default=datetime.now)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    destination_type = models.TextField(
        db_column='DestinationType', max_length=10, null=True, default=None)
    acc_rate_dock = models.BooleanField(
        db_column='AccRateDock', default=1)
    acc_rate_DOE_factorA = models.DecimalField(
        db_column='AccRateDOEFactorA', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_DOE_factorB = models.DecimalField(
        db_column='AccRateDOEFactorB', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_elevator = models.BooleanField(
        db_column='AccRateElevator', default=False)
    acc_rate_exclude_legs = models.BooleanField(
        db_column='AccRateExcludeLegs', default=False)
    acc_rate_extra_stop_rates = models.TextField(
        db_column='AccRateExtraStopRates', max_length=4000, null=True, default=None)
    acc_rate_factor_id = models.ForeignKey(
        AccFactor, db_column='AccRateFactorID', on_delete=models.CASCADE, related_name='+', default=1)
    acc_rate_increment = models.DecimalField(
        db_column='AccRateIncrement', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_fuel_price_average = models.TextField(
        db_column='AccRateFuelPriceAverage', max_length=10, null=True, default=None)
    acc_rate_max_charge = models.DecimalField(
        db_column='AccRateMaxCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_min_charge = models.DecimalField(
        db_column='AccRateMinCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_percent = models.DecimalField(
        db_column='AccRatePercent', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field1ID = models.ForeignKey(
        AccRangeType, db_column='AccRangeTypeID', on_delete=models.CASCADE, related_name='+')
    acc_rate_range_type_id = models.BigIntegerField(
        db_column='AccRateRangeTypeID', default=1, null=True)
    min_shipment_value = models.DecimalField(
        db_column='MinShipmentValue', decimal_places=6, max_digits=19, null=True, default=None)
    max_shipment_value = models.DecimalField(
        db_column='MaxShipmentValue', decimal_places=6, max_digits=19, null=True, default=None)
    min_weight_value = models.DecimalField(
        db_column='MinWeightValue', decimal_places=6, max_digits=19, null=True, default=None)
    max_weight_value = models.DecimalField(
        db_column='MaxWeightValue', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_shipping_instructionID = models.BigIntegerField(
        db_column='AccRateShippingInstructionID', default=None, null=True)
    acc_rate_survey = models.BooleanField(
        db_column='AccRateSurvey', default=False)
    acc_rate_stairs = models.BooleanField(
        db_column='AccRateStairs', default=False)
    acc_rate_status_code = models.TextField(
        db_column='AccRateStatusCode', max_length=10, null=True, default=None)
    acc_rate_threshold_amount = models.DecimalField(
        db_column='AccRateThresholdAmount', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_vehicle_restricted = models.BooleanField(
        db_column='AccRateVehicleRestricted', default=False)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, null=True, related_name='+')
    acc_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="OriginTypeID", related_name="+")
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="DestinationTypeID", related_name="+")
    request_section_id = models.ForeignKey(
        RequestSection, db_column='RequestSectionID', null=True, on_delete=models.CASCADE, related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_override_id)

    class Meta:
        unique_together = ((
            'request_id', 'acc_header_id', 'origin_id', 'origin_type_id', 'destination_id', 'destination_type_id',
            'request_section_id'))
        verbose_name_plural = 'AccessorialOverride'
        db_table = 'AccessorialOverride'


class AccessorialOverrideHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_override_id = models.ForeignKey(
        AccessorialOverride, db_column='AccOverrideID', on_delete=models.CASCADE, related_name='+')
    acc_override_version_id = models.BigAutoField(
        db_column='AccOverrideVersionID', primary_key=True, serialize=False)
    tmacc_override_id = models.BigIntegerField(
        db_column='TMAccOverrideID', default=None)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    request_version_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    allow_between = models.BooleanField(
        db_column='AllowBetween', default=False)
    carrier_movement_type = models.TextField(
        db_column='CarrierMovementType', max_length=1, null=True, default=None)
    commodity_version_id = models.ForeignKey(
        CommodityHistory, db_column='CommodityVersionID', on_delete=models.CASCADE, null=True, related_name='+')
    acc_rate_custom_maximum = models.DecimalField(
        db_column='AccRateCustomMaximum', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_custom_minimum = models.DecimalField(
        db_column='AccRateCustomMinimum', decimal_places=6, max_digits=19, null=True, default=None)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', null=True, default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', null=True, default=None)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    destination_type = models.TextField(
        db_column='DestinationType', max_length=10, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE, null=True,
        related_name='+')
    acc_rate_dock = models.BooleanField(
        db_column='AccRateDock', default=False)
    acc_rate_DOE_factorA = models.DecimalField(
        db_column='AccRateDOEFactorA', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_DOE_factorB = models.DecimalField(
        db_column='AccRateDOEFactorB', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_elevator = models.BooleanField(
        db_column='AccRateElevator', default=False)
    acc_rate_exclude_legs = models.BooleanField(
        db_column='AccRateExcludeLegs', default=False)
    acc_rate_extra_stop_rates = models.TextField(
        db_column='AccRateExtraStopRates', max_length=4000, null=True, default=None)
    acc_rate_increment = models.DecimalField(
        db_column='AccRateIncrement', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_fuel_price_average = models.TextField(
        db_column='AccRateFuelPriceAverage', max_length=10, null=True, default=None)
    acc_rate_max_charge = models.DecimalField(
        db_column='AccRateMaxCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_min_charge = models.DecimalField(
        db_column='AccRateMinCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_percent = models.DecimalField(
        db_column='AccRatePercent', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_range_field_version1_id = models.BigIntegerField(
        db_column='AccRateRangeFieldVersion1ID', default=None, null=True)
    acc_rate_range_field_version2_id = models.BigIntegerField(
        db_column='AccRateRangeFieldVersion2ID', default=None, null=True)
    acc_rate_range_type_version_id = models.BigIntegerField(
        db_column='AccRateRangeTypeVersionID', default=1, null=True)
    min_shipment_value = models.DecimalField(
        db_column='MinShipmentValue', decimal_places=6, max_digits=19, null=True, default=None)
    max_shipment_value = models.DecimalField(
        db_column='MaxShipmentValue', decimal_places=6, max_digits=19, null=True, default=None)
    min_weight_value = models.DecimalField(
        db_column='MinWeightValue', decimal_places=6, max_digits=19, null=True, default=None)
    max_weight_value = models.DecimalField(
        db_column='MaxWeightValue', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_shipping_instructionID = models.BigIntegerField(
        db_column='AccRateShippingInstructionID', default=None, null=True)
    acc_rate_survey = models.BooleanField(
        db_column='AccRateSurvey', default=False)
    acc_rate_stairs = models.BooleanField(
        db_column='AccRateStairs', default=False)
    acc_rate_status_code = models.TextField(
        db_column='AccRateStatusCode', max_length=10, null=True, default=None)
    acc_rate_threshold_amount = models.DecimalField(
        db_column='AccRateThresholdAmount', decimal_places=6, max_digits=19, null=True, default=None)
    acc_rate_vehicle_restricted = models.BooleanField(
        db_column='AccRateVehicleRestricted', default=False)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="OriginTypeVersionID",
        related_name="+")
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTypeVersionID",
        related_name="+")
    request_section_version_id = models.ForeignKey(
        RequestSectionHistory, db_column='RequestSectionVersionID', null=True, on_delete=models.CASCADE,
        related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_override_version_id)

    class Meta:
        index_together = (("acc_override_id", "version_num"))
        verbose_name_plural = 'AccessorialOverride_History'
        db_table = 'AccessorialOverride_History'


class AccessorialDetentionOverride(Delete):
    acc_detention_override_id = models.BigAutoField(
        db_column='AccDetentionOverrideID', primary_key=True, serialize=False)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE, related_name='+')
    tm_detention_override_id = models.BigIntegerField(
        db_column='TMDetentionOverrideID', default=None)
    request_id = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    currency_id = models.ForeignKey(
        Currency, db_column='CurrencyID', on_delete=models.CASCADE, related_name='+', default=1)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    detention_type = models.TextField(
        db_column='DetentionType', max_length=10, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=datetime.now)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=datetime.now)
    equipment_type_id = models.ForeignKey(
        EquipmentType, db_column='EquipmentTypeID', on_delete=models.CASCADE, related_name='+', default=1)
    exclude_closed_days_detention = models.TextField(
        db_column='ExcludeClosedDaysDetention', max_length=20, null=True, default=None)
    exclude_closed_days_freetime = models.TextField(
        db_column='ExcludeClosedDaysFreeTime', max_length=20, null=True, default=None)
    fb_based_date_field = models.TextField(
        db_column='FBBasedDateField', max_length=10, null=True, default=None)
    free_time_id = models.ForeignKey(
        FreeTime, db_column='FreeTimeID', on_delete=models.CASCADE, related_name='+')
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=3, null=True, default=None)
    freetime_unit_to_measure = models.TextField(
        db_column='FreeTimeUnitofMeasure', max_length=10, null=True, default=None)
    inter_company = models.TextField(
        db_column='InterCompany', max_length=5, null=True, default=None)
    late_no_bill = models.TextField(
        db_column='LateNoBill', max_length=5, null=True, default=None)
    late_window = models.DecimalField(
        db_column='LateWindow', decimal_places=6, max_digits=19, null=True, default=None)
    ltl_proration_method = models.TextField(
        db_column='LtlProrationMethod', max_length=10, null=True, default=None)
    max_bill_time = models.DecimalField(
        db_column='MaxBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_bill_time = models.DecimalField(
        db_column='MinBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    free_times = models.TextField(
        db_column='FreeTimes', max_length=4000, null=True, default=None)
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, related_name='+')
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    payment_option = models.TextField(
        db_column='PaymentOption', max_length=10, null=True, default=None)
    second_bill_rate = models.DecimalField(
        db_column='SecondBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    shipper = models.TextField(
        db_column='Shipper', max_length=10, null=True, default=None)
    shipper_group = models.TextField(
        db_column='ShipperGroup', max_length=10, null=True, default=None)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    destination_type = models.TextField(
        db_column='DestinationType', max_length=40, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    start_bill_rate = models.DecimalField(
        db_column='StartBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    start_option = models.TextField(
        db_column='StartOption', max_length=40, null=True, default=None)
    stop_option = models.TextField(
        db_column='StopOption', max_length=40, null=True, default=None)
    use_actual_time = models.BooleanField(
        db_column='UseActualTime', default=False)
    warning_send = models.TextField(
        db_column='WarningSend', max_length=5, null=True, default=None)
    warning_time = models.DecimalField(
        db_column='WarningTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_detention_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccDetentionOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="OriginTypeID", related_name="+")
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, null=True, default=1, db_column="DestinationTypeID", related_name="+")
    request_section_id = models.ForeignKey(
        RequestSection, db_column='RequestSectionID', null=True, on_delete=models.CASCADE, related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_detention_override_id)

    class Meta:
        verbose_name_plural = 'AccessorialDetentionOverride'
        db_table = 'AccessorialDetentionOverride'


class AccessorialDetentionOverrideHistory(Delete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_detention_override_version_id = models.BigAutoField(
        db_column='AccDetentionOverrideVersionID', primary_key=True, serialize=False)
    acc_detention_override_id = models.ForeignKey(
        AccessorialDetentionOverride, db_column='AccDetentionOverrideID', on_delete=models.CASCADE)
    tm_detention_override_id = models.BigIntegerField(
        db_column='TMDetentionOverrideID', default=None)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    request_version_id = models.ForeignKey(
        Request, db_column='RequestVersionID', on_delete=models.CASCADE, related_name='+')
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    currency_version_id = models.ForeignKey(
        CurrencyHistory, db_column='CurrencyVersionID', on_delete=models.CASCADE, related_name='+')
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    detention_type = models.TextField(
        db_column='DetentionType', max_length=10, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    equipment_type_version_id = models.ForeignKey(
        EquipmentTypeHistory, db_column='EquipmentTypeVersionID', on_delete=models.CASCADE, related_name='+')
    exclude_closed_days_detention = models.TextField(
        db_column='ExcludeClosedDaysDetention', max_length=20, null=True, default=None)
    exclude_closed_days_freetime = models.TextField(
        db_column='ExcludeClosedDaysFreeTime', max_length=20, null=True, default=None)
    fb_based_date_field = models.TextField(
        db_column='FBBasedDateField', max_length=10, null=True, default=None)
    free_time_version_id = models.ForeignKey(
        FreeTimeHistory, db_column='FreeTimeVersionID', on_delete=models.CASCADE, related_name='+', default=None)
    free_time_unit = models.TextField(
        db_column='FreeTimeUnit', max_length=3, null=True, default=None)
    freetime_unit_to_measure = models.TextField(
        db_column='FreeTimeUnitofMeasure', max_length=10, null=True, default=None)
    inter_company = models.TextField(
        db_column='InterCompany', max_length=5, null=True, default=None)
    late_no_bill = models.TextField(
        db_column='LateNoBill', max_length=5, null=True, default=None)
    late_window = models.DecimalField(
        db_column='LateWindow', decimal_places=6, max_digits=19, null=True, default=None)
    ltl_proration_method = models.TextField(
        db_column='LtlProrationMethod', max_length=10, null=True, default=None)
    max_bill_time = models.DecimalField(
        db_column='MaxBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_bill_time = models.DecimalField(
        db_column='MinBillTime', decimal_places=6, max_digits=19, null=True, default=None)
    free_times = models.TextField(
        db_column='FreeTimes', max_length=4000, null=True, default=None)
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    payment_option = models.TextField(
        db_column='PaymentOption', max_length=10, null=True, default=None)
    second_bill_rate = models.DecimalField(
        db_column='SecondBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    shipper = models.TextField(
        db_column='Shipper', max_length=10, null=True, default=None)
    shipper_group = models.TextField(
        db_column='ShipperGroup', max_length=10, null=True, default=None)
    origin_type = models.TextField(
        db_column='OriginType', max_length=10, null=True, default=None)
    destination_type = models.TextField(
        db_column='DestinationType', max_length=40, null=True, default=None)
    origin_id = models.BigIntegerField(null=True, default=1, db_column="OriginID")
    destination_id = models.BigIntegerField(null=True, default=1, db_column="DestinationID")
    start_bill_rate = models.DecimalField(
        db_column='StartBillRate', decimal_places=6, max_digits=19, null=True, default=None)
    start_option = models.TextField(
        db_column='StartOption', max_length=40, null=True, default=None)
    stop_option = models.TextField(
        db_column='StopOption', max_length=40, null=True, default=None)
    use_actual_time = models.BooleanField(
        db_column='UseActualTime', default=False)
    warning_send = models.TextField(
        db_column='WarningSend', max_length=5, null=True, default=None)
    warning_time = models.DecimalField(
        db_column='WarningTime', decimal_places=6, max_digits=19, null=True, default=None)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_detention_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccDetentionOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="OriginTypeVersionID",
        related_name="+")
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTypeVersionID",
        related_name="+")
    request_section_version_id = models.ForeignKey(
        RequestSectionHistory, db_column='RequestSectionVersionID', null=True, on_delete=models.CASCADE,
        related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_detention_override_version_id)

    class Meta:
        index_together = (("acc_detention_override_id", "version_num"))
        verbose_name_plural = 'AccessorialDetentionOverride_History'
        db_table = 'AccessorialDetentionOverride_History'


class AccessorialStorageOverride(Delete):
    acc_storage_override_id = models.BigAutoField(
        db_column='AccStorageOverrideID', primary_key=True, serialize=False)
    tm_storage_override_id = models.BigIntegerField(
        db_column='TMStorageOverrideID', default=1)
    acc_header_id = models.ForeignKey(
        AccessorialHeader, db_column='AccHeaderID', on_delete=models.CASCADE)
    request_id = models.ForeignKey(
        Request, db_column='RequestID', on_delete=models.CASCADE)
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    bill_option = models.TextField(
        db_column='BillOption', max_length=1, null=True, default=None)
    currency_id = models.ForeignKey(
        Currency, db_column='CurrencyID', on_delete=models.CASCADE, related_name='+', default=1)
    dangerous_goods = models.BooleanField(
        db_column='DangerousGoods', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=datetime.now)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=datetime.now)
    free_days = models.BigIntegerField(
        db_column='FreeDays', default=None)
    high_value = models.BooleanField(
        db_column='HighValue', default=False)
    include_delivery_day = models.BooleanField(
        db_column='IncludeDeliveryDay', default=False)
    include_terminal_service_calendar = models.BooleanField(
        db_column='IncludeTerminalServiceCalendar', default=False)
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    rate_amount = models.DecimalField(
        db_column='RateAmount', decimal_places=6, max_digits=19, null=True, default=None)
    rate_max = models.DecimalField(
        db_column='RateMax', decimal_places=6, max_digits=19, null=True, default=None)
    rate_min = models.DecimalField(
        db_column='RateMin', decimal_places=6, max_digits=19, null=True, default=None)
    rate_per = models.DecimalField(
        db_column='RatePer', decimal_places=6, max_digits=19, null=True, default=None)
    temp_controlled = models.BooleanField(
        db_column='TempControlled', default=False)
    unit_id = models.ForeignKey(
        Unit, db_column='UnitID', on_delete=models.CASCADE, related_name='+', default=1)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_storage_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccStorageOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    request_section_id = models.ForeignKey(
        RequestSection, db_column='RequestSectionID', null=True, on_delete=models.CASCADE, related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_storage_override_id)

    class Meta:
        verbose_name_plural = 'AccessorialStorageOverride'
        db_table = 'AccessorialStorageOverride'


class AccessorialStorageOverrideHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_storage_override_id = models.ForeignKey(
        AccessorialStorage, db_column='AccStorageOverrideID', on_delete=models.CASCADE)
    acc_storage_override_version_id = models.BigAutoField(
        db_column='AccStorageOverrideVersionID', primary_key=True, serialize=False)
    tm_storage_override_id = models.BigIntegerField(
        db_column='TMStorageOverrideID', default=None)
    acc_header_version_id = models.ForeignKey(
        AccessorialHeaderHistory, db_column='AccHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    request_version_id = models.ForeignKey(
        RequestHistory, db_column='RequestVersionID', on_delete=models.CASCADE, related_name='+')
    base_rate = models.BooleanField(
        db_column='BaseRate', default=False)
    bill_option = models.TextField(
        db_column='BillOption', max_length=1, null=True, default=None)
    currency_version_id = models.ForeignKey(
        CurrencyHistory, db_column='CurrencyVersionID', on_delete=models.CASCADE, related_name='+')
    dangerous_goods = models.BooleanField(
        db_column='DangerousGoods', default=False)
    description = models.TextField(
        db_column='Description', max_length=40, null=True, default=None)
    effective_from = models.DateTimeField(
        db_column='EffectiveFrom', default=None)
    effective_to = models.DateTimeField(
        db_column='EffectiveTo', default=None)
    free_days = models.BigIntegerField(
        db_column='FreeDays', default=None)
    high_value = models.BooleanField(
        db_column='HighValue', default=False)
    include_delivery_day = models.BooleanField(
        db_column='IncludeDeliveryDay', default=False)
    include_terminal_service_calendar = models.BooleanField(
        db_column='IncludeTerminalServiceCalendar', default=False)
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE)
    operations_code = models.TextField(
        db_column='OperationsCode', max_length=10, null=True, default=None)
    rate_amount = models.DecimalField(
        db_column='RateAmount', decimal_places=6, max_digits=19, null=True, default=None)
    rate_max = models.DecimalField(
        db_column='RateMax', decimal_places=6, max_digits=19, null=True, default=None)
    rate_min = models.DecimalField(
        db_column='RateMin', decimal_places=6, max_digits=19, null=True, default=None)
    rate_per = models.DecimalField(
        db_column='RatePer', decimal_places=6, max_digits=19, null=True, default=None)
    unit_version_id = models.ForeignKey(
        UnitHistory, db_column='UnitVersionID', on_delete=models.CASCADE, related_name='+')
    temp_controlled = models.BooleanField(
        db_column='TempControlled', default=False)
    min_std_charge = models.DecimalField(
        db_column='MinStdCharge', decimal_places=6, max_digits=19, null=True, default=None)
    acc_storage_override_source_id = models.BigIntegerField(
        null=True, blank=False, db_column="AccStorageOverrideSourceID")
    usage_percentage = models.DecimalField(
        db_column='UsagePercentage', decimal_places=6, max_digits=19, null=True, default=None)
    is_waive = models.BooleanField(
        db_column='isWaive', default=False)
    request_section_version_id = models.ForeignKey(
        RequestSectionHistory, db_column='RequestSectionVersionID', null=True, on_delete=models.CASCADE,
        related_name='+')
    tmid = models.IntegerField(
        db_column='TMID', null=True, default=None)

    def __str__(self):
        return str(self.acc_storage_override_version_id)

    class Meta:
        index_together = (("acc_storage_override_id", "version_num"))
        verbose_name_plural = 'AccessorialStorageOverride_History'
        db_table = 'AccessorialStorageOverride_History'


class Terms(Delete):
    acc_term_id = models.BigAutoField(
        db_column='AccTermID', primary_key=True, serialize=False)
    request_id = models.ForeignKey(
        Request, db_column='RequestID', on_delete=models.CASCADE)
    custom_terms = models.TextField(
        db_column='CustomTerms', max_length=4000, null=True, default=None)
    status = models.BooleanField(
        db_column='Status', default=False)

    def __str__(self):
        return str(self.acc_term_id)

    class Meta:
        verbose_name_plural = 'Terms'
        db_table = 'Terms'


class TermsHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    acc_term_id = models.ForeignKey(
        Terms, db_column='AccTermID', on_delete=models.CASCADE)
    acc_term_version_id = models.BigAutoField(
        db_column='AccTermVersionID', primary_key=True, serialize=False)
    request_version_id = models.ForeignKey(
        RequestHistory, db_column='RequestVersionID', on_delete=models.CASCADE, related_name='+')
    custom_terms = models.TextField(
        db_column='CustomTerms', max_length=4000, null=True, default=None)
    status = models.BooleanField(
        db_column='Status', default=False)

    def __str__(self):
        return str(self.acc_term_version_id)

    class Meta:
        index_together = (("acc_term_id", "version_num"))
        verbose_name_plural = 'Terms_History'
        db_table = 'Terms_History'


class InterlinerCosts(Delete):
    interliner_cost_id = models.BigAutoField(
        db_column='InterlinerCostID', primary_key=True, serialize=False)
    rate_sheet_id = models.TextField(
        db_column='RateSheetID', max_length=50, null=True, default=None)
    rate_sheet_name = models.TextField(
        db_column='RateSheetName', max_length=4000, null=True, default=None)
    vendor_id = models.TextField(
        db_column='VendorID', max_length=50, null=True, default=None)
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, db_column='SubServiceLevelID', on_delete=models.CASCADE, related_name='+')
    weight_breaker_header_id = models.ForeignKey(
        WeightBreakHeader, db_column='WeightBreakHeaderID', on_delete=models.CASCADE, related_name='+')
    as_rating = models.BooleanField(
        db_column='AsRating', default=False)
    unit_id = models.ForeignKey(
        Unit, on_delete=models.CASCADE, db_column="UnitID")
    unit_symbol_id = models.BigIntegerField(db_column='UnitSymbolID', default=None)
    unit_factor = models.DecimalField(
        db_column='UnitFactor', decimal_places=6, max_digits=19, null=True, default=None)
    is_between = models.BooleanField(
        db_column='IsBetween', default=False)
    customer_discount = models.DecimalField(
        db_column='CustomerDiscount', decimal_places=6, max_digits=19, null=True, default=None)
    currency_id = models.ForeignKey(
        Currency, on_delete=models.CASCADE, db_column="CurrencyID")
    cost = models.TextField(
        db_column='Cost', max_length=4000, null=True, default=None)
    destination_id = models.BigIntegerField(db_column='DestinationID', default=None)
    destination_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, db_column="DestinationTypeID", related_name='+')
    origin_id = models.BigIntegerField(db_column='OriginID', default=None)
    origin_type_id = models.ForeignKey(
        PointType, on_delete=models.CASCADE, db_column="OriginTypeID", related_name='+')
    direction = models.TextField(
        db_column='Direction', max_length=50, null=True, default=None)
    equipment_type_id = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeID")

    def __str__(self):
        return str(self.interliner_cost_id)

    class Meta:
        verbose_name_plural = 'InterlinerCosts'
        db_table = 'InterlinerCosts'


class InterlinerCostsHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    rate_sheet_id = models.ForeignKey(
        InterlinerCosts, db_column='RateSheetID', on_delete=models.CASCADE)
    rate_sheet_version_id = models.BigAutoField(
        db_column='RateSheetVersionID', primary_key=True, serialize=False)
    rate_sheet_name = models.TextField(
        db_column='RateSheetName', max_length=4000, null=True, default=None)
    vendor_id = models.TextField(
        db_column='VendorID', max_length=50, null=True, default=None)
    sub_service_level_version_id = models.ForeignKey(
        SubServiceLevelHistory, db_column='SubServiceLevelVersionID', on_delete=models.CASCADE, related_name='+')
    weight_break_header_version_id = models.ForeignKey(
        WeightBreakHeaderHistory, db_column='WeightBreakHeaderVersionID', on_delete=models.CASCADE, related_name='+')
    as_rating = models.BooleanField(
        db_column='AsRating', default=False)
    unit_version_id = models.ForeignKey(
        UnitHistory, on_delete=models.CASCADE, db_column="UnitVersionID")
    unit_symbol_id = models.BigIntegerField(db_column='UnitSymbolID', default=None)
    unit_factor = models.DecimalField(
        db_column='UnitFactor', decimal_places=6, max_digits=19, null=True, default=None)
    is_between = models.BooleanField(
        db_column='IsBetween', default=False)
    customer_discount = models.DecimalField(
        db_column='CustomerDiscount', decimal_places=6, max_digits=19, null=True, default=None)
    currency_version_id = models.ForeignKey(
        CurrencyHistory, on_delete=models.CASCADE, db_column="CurrencyVersionID")
    cost = models.TextField(
        db_column='Cost', max_length=4000, null=True, default=None)
    destination_id = models.BigIntegerField(db_column='DestinationID', default=None)
    destination_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, db_column="DestinationTypeVersionID", related_name='+')
    origin_id = models.BigIntegerField(db_column='OriginID', default=None)
    origin_type_version_id = models.ForeignKey(
        PointTypeHistory, on_delete=models.CASCADE, db_column="OriginTypeVersionID", related_name='+')
    direction = models.TextField(
        db_column='Direction', max_length=50, null=True, default=None)
    equipment_type_version_id = models.ForeignKey(
        EquipmentTypeHistory, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeVersionID")

    def __str__(self):
        return str(self.rate_sheet_version_id)

    class Meta:
        index_together = (("rate_sheet_id", "version_num"))
        verbose_name_plural = 'InterlinerCosts_History'
        db_table = 'InterlinerCosts_History'


class LaneType(Delete):
    lane_type_id = models.BigAutoField(
        db_column='LaneTypeID', primary_key=True, serialize=False)
    lane_type_name = models.TextField(
        db_column='LaneTypeName', max_length=50, null=True, default=None)

    def __str__(self):
        return str(self.lane_type_id)

    class Meta:
        verbose_name_plural = 'LaneType'
        db_table = 'LaneType'


class LaneTypeHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    lane_type_id = models.ForeignKey(
        LaneType, db_column='LaneTypeID', on_delete=models.CASCADE, related_name='+')
    lane_type_version_id = models.BigAutoField(
        db_column='LaneTypeVersionID', primary_key=True, serialize=False)
    lane_type_nName = models.TextField(
        db_column='LaneTypeName', max_length=50, null=True, default=None)

    def __str__(self):
        return str(self.lane_type_version_id)

    class Meta:
        index_together = (("lane_type_id", "version_num"))
        verbose_name_plural = 'LaneType_History'
        db_table = 'LaneType_History'


class SalesIncentive(Delete):
    sales_incentive_id = models.BigAutoField(
        db_column='SalesIncentiveID', primary_key=True, serialize=False)
    sales_incentive_type = models.TextField(
        db_column='SalesIncentiveType', max_length=50, null=True, default=None)

    def __str__(self):
        return str(self.sales_incentive_id)

    class Meta:
        verbose_name_plural = 'SalesIncentive'
        db_table = 'SalesIncentive'


class SalesIncentiveHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    sales_incentive_id = models.ForeignKey(
        SalesIncentive, db_column='SalesIncentiveID', on_delete=models.CASCADE, related_name='+')
    sales_incentive_type = models.TextField(
        db_column='SalesIncentiveType', max_length=50, null=True, default=None)
    sales_incentive_version_id = models.BigAutoField(
        db_column='SalesIncentiveVersionID', primary_key=True, serialize=False)

    def __str__(self):
        return str(self.sales_incentive_version_id)

    class Meta:
        index_together = (("sales_incentive_id", "version_num"))
        verbose_name_plural = 'SalesIncentive_History'
        db_table = 'SalesIncentive_History'


class Review(Delete):
    review_id = models.BigAutoField(
        db_column='ReviewID', primary_key=True, serialize=False)
    review_type = models.TextField(
        db_column='ReviewType', max_length=50, null=True, default=None)
    request_id = models.OneToOneField(
        Request, db_column='RequestID', unique=True, on_delete=models.CASCADE, related_name='+')
    average_shipment_size = models.DecimalField(
        db_column='AverageShipmentSize', decimal_places=3, max_digits=10, null=True, default=None)
    average_shipment_density = models.DecimalField(
        db_column='AverageShipmentDensity', decimal_places=3, max_digits=10, null=True, default=None)
    monthly_shipment_value = models.DecimalField(
        db_column='MonthlyShipmentValue', decimal_places=3, max_digits=10, null=True, default=None)
    sales_incentive_id = models.ForeignKey(
        SalesIncentive, db_column='SalesIncentiveID', on_delete=models.CASCADE, related_name='+')
    review_eff_date = models.DateTimeField(db_column='ReviewEffDate', null=True, default=None)
    review_exp_date = models.DateTimeField(db_column='ReviewExpDate', null=True, default=None)
    pricing_rate_change_dol = models.TextField(
        db_column='PricingRateChangeDol', max_length=50, null=True, default=None)
    pricing_rate_change_per = models.TextField(
        db_column='PricingRateChangePer', max_length=50, null=True, default=None)
    sales_rate_change_dol = models.TextField(
        db_column='SalesRateChangeDol', max_length=50, null=True, default=None)
    sales_rate_change_per = models.TextField(
        db_column='SalesRateChangePer', max_length=50, null=True, default=None)

    def __str__(self):
        return str(self.review_id)

    class Meta:
        verbose_name_plural = 'Review'
        db_table = 'Review'


class ReviewHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    review_id = models.ForeignKey(
        Review, db_column='ReviewID', on_delete=models.CASCADE, related_name='+')
    review_type = models.TextField(
        db_column='ReviewType', max_length=50, null=True, default=None)
    review_version_id = models.BigAutoField(
        db_column='ReviewVersionID', primary_key=True, serialize=False)
    request_version_id = models.ForeignKey(
        RequestHistory, db_column='RequestVersionID', on_delete=models.CASCADE, related_name='+')
    average_shipment_size = models.DecimalField(
        db_column='AverageShipmentSize', decimal_places=3, max_digits=10, null=True, default=None)
    average_shipment_density = models.DecimalField(
        db_column='AverageShipmentDensity', decimal_places=3, max_digits=10, null=True, default=None)
    monthly_shipment_value = models.DecimalField(
        db_column='MonthlyShipmentValue', decimal_places=3, max_digits=10, null=True, default=None)
    sales_incentive_version_id = models.ForeignKey(
        SalesIncentiveHistory, db_column='SalesIncentiveVersionID', on_delete=models.CASCADE, related_name='+')
    review_eff_date = models.DateTimeField(db_column='ReviewEffDate', null=True, default=None)
    review_exp_date = models.DateTimeField(db_column='ReviewExpDate', null=True, default=None)
    pricing_rate_change_dol = models.TextField(
        db_column='PricingRateChangeDol', max_length=50, null=True, default=None)
    pricing_rate_change_per = models.TextField(
        db_column='PricingRateChangePer', max_length=50, null=True, default=None)
    sales_rate_change_dol = models.TextField(
        db_column='SalesRateChangeDol', max_length=50, null=True, default=None)
    sales_rate_change_per = models.TextField(
        db_column='SalesRateChangePer', max_length=50, null=True, default=None)

    def __str__(self):
        return str(self.review_version_id)

    class Meta:
        index_together = (("review_id", "version_num"))
        verbose_name_plural = 'Review_History'
        db_table = 'Review_History'


class ProfitLossSummary(Delete):
    profit_loss_summary_id = models.BigAutoField(
        db_column='ProfitLossSummaryID', primary_key=True, serialize=False)
    lane_type_id = models.ForeignKey(
        LaneType, db_column='LaneTypeID', on_delete=models.CASCADE, related_name='+')
    num_freight_bills = models.DecimalField(
        db_column='NumFreightBills', decimal_places=6, max_digits=19, null=True, default=None)
    billed_weight = models.DecimalField(
        db_column='BilledWeight', decimal_places=6, max_digits=19, null=True, default=None)
    revenue = models.DecimalField(
        db_column='Revenue', decimal_places=6, max_digits=19, null=True, default=None)
    cost = models.DecimalField(
        db_column='Cost', decimal_places=6, max_digits=19, null=True, default=None)
    profit = models.DecimalField(
        db_column='Profit', decimal_places=6, max_digits=19, null=True, default=None)
    margin = models.DecimalField(
        db_column='Margin', decimal_places=6, max_digits=19, null=True, default=None)
    required_increase = models.DecimalField(
        db_column='RequiredIncrease', decimal_places=6, max_digits=19, null=True, default=None)
    review_id = models.ForeignKey(
        Review, db_column='ReviewID', on_delete=models.CASCADE, default=None, related_name='+')

    def __str__(self):
        return str(self.profit_loss_summary_id)

    class Meta:
        verbose_name_plural = 'ProfitLossSummary'
        db_table = 'ProfitLossSummary'


class ProfitLossSummaryHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    profit_loss_summary_id = models.ForeignKey(
        ProfitLossSummary, db_column='ProfitLossSummaryID', on_delete=models.CASCADE, related_name='+')
    profit_loss_summary_version_id = models.BigAutoField(
        db_column='ProfitLossSummaryVersionID', primary_key=True, serialize=False)
    lane_type_version_id = models.ForeignKey(
        LaneTypeHistory, db_column='LaneTypeVersionID', on_delete=models.CASCADE, related_name='+')
    num_freight_bills = models.DecimalField(
        db_column='NumFreightBills', decimal_places=6, max_digits=19, null=True, default=None)
    billed_weight = models.DecimalField(
        db_column='BilledWeight', decimal_places=6, max_digits=19, null=True, default=None)
    revenue = models.DecimalField(
        db_column='Revenue', decimal_places=6, max_digits=19, null=True, default=None)
    cost = models.DecimalField(
        db_column='Cost', decimal_places=6, max_digits=19, null=True, default=None)
    profit = models.DecimalField(
        db_column='Profit', decimal_places=6, max_digits=19, null=True, default=None)
    margin = models.DecimalField(
        db_column='Margin', decimal_places=6, max_digits=19, null=True, default=None)
    required_increase = models.DecimalField(
        db_column='RequiredIncrease', decimal_places=6, max_digits=19, null=True, default=None)
    review_version_id = models.ForeignKey(
        ReviewHistory, db_column='ReviewVersionID', on_delete=models.CASCADE, default=None, related_name='+')

    def __str__(self):
        return str(self.profit_loss_summary_version_id)

    class Meta:
        index_together = (("profit_loss_summary_id", "version_num"))
        verbose_name_plural = 'ProfitLossSummary_History'
        db_table = 'ProfitLossSummary_History'


class RevenueHistory(Delete):
    revenue_history_id = models.BigAutoField(
        db_column='RevenueHistoryID', primary_key=True, serialize=False)
    period = models.DecimalField(
        db_column='Period', decimal_places=6, max_digits=19, null=True, default=None)
    num_pickups = models.DecimalField(
        db_column='NumPickups', decimal_places=6, max_digits=19, null=True, default=None)
    num_freight_bills = models.DecimalField(
        db_column='NumFreightBills', decimal_places=6, max_digits=19, null=True, default=None)
    billed_weight = models.DecimalField(
        db_column='BilledWeight', decimal_places=6, max_digits=19, null=True, default=None)
    average_weight = models.DecimalField(
        db_column='AverageWeight', decimal_places=6, max_digits=19, null=True, default=None)
    average_density = models.DecimalField(
        db_column='AverageDensity', decimal_places=6, max_digits=19, null=True, default=None)
    monthly_revenue = models.DecimalField(
        db_column='MonthlyRevenue', decimal_places=6, max_digits=19, null=True, default=None)
    fixed_costs = models.DecimalField(
        db_column='FixedCosts', decimal_places=6, max_digits=19, null=True, default=None)
    variable_costs = models.DecimalField(
        db_column='VariableCosts', decimal_places=6, max_digits=19, null=True, default=None)
    total_costs = models.DecimalField(
        db_column='TotalCosts', decimal_places=6, max_digits=19, null=True, default=None)
    profit = models.DecimalField(
        db_column='Profit', decimal_places=6, max_digits=19, null=True, default=None)
    margin = models.DecimalField(
        db_column='Margin', decimal_places=6, max_digits=19, null=True, default=None)
    review_id = models.ForeignKey(
        Review, db_column='ReviewID', on_delete=models.CASCADE, default=None, related_name='+')

    def __str__(self):
        return str(self.revenue_history_id)

    class Meta:
        verbose_name_plural = 'RevenueHistory'
        db_table = 'RevenueHistory'


class RevenueHistoryHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    revenue_history_id = models.ForeignKey(
        RevenueHistory, db_column='RevenueHistoryID', on_delete=models.CASCADE, related_name='+')
    revenue_history_version_id = models.BigAutoField(
        db_column='RevenueHistoryVersionID', primary_key=True, serialize=False)
    period = models.DecimalField(
        db_column='Period', decimal_places=6, max_digits=19, null=True, default=None)
    num_pickups = models.DecimalField(
        db_column='NumPickups', decimal_places=6, max_digits=19, null=True, default=None)
    num_freight_bills = models.DecimalField(
        db_column='NumFreightBills', decimal_places=6, max_digits=19, null=True, default=None)
    billed_weight = models.DecimalField(
        db_column='BilledWeight', decimal_places=6, max_digits=19, null=True, default=None)
    average_weight = models.DecimalField(
        db_column='AverageWeight', decimal_places=6, max_digits=19, null=True, default=None)
    average_density = models.DecimalField(
        db_column='AverageDensity', decimal_places=6, max_digits=19, null=True, default=None)
    monthly_revenue = models.DecimalField(
        db_column='MonthlyRevenue', decimal_places=6, max_digits=19, null=True, default=None)
    fixed_costs = models.DecimalField(
        db_column='FixedCosts', decimal_places=6, max_digits=19, null=True, default=None)
    variable_costs = models.DecimalField(
        db_column='VariableCosts', decimal_places=6, max_digits=19, null=True, default=None)
    total_costs = models.DecimalField(
        db_column='TotalCosts', decimal_places=6, max_digits=19, null=True, default=None)
    profit = models.DecimalField(
        db_column='Profit', decimal_places=6, max_digits=19, null=True, default=None)
    margin = models.DecimalField(
        db_column='Margin', decimal_places=6, max_digits=19, null=True, default=None)
    review_version_id = models.ForeignKey(
        ReviewHistory, db_column='ReviewVersionID', on_delete=models.CASCADE, default=None, related_name='+')

    def __str__(self):
        return str(self.revenue_history_version_id)

    class Meta:
        index_together = (("revenue_history_id", "version_num"))
        verbose_name_plural = 'RevenueHistory_History'
        db_table = 'RevenueHistory_History'


class RevenueBreakdown(Delete):
    revenue_breakdown_id = models.BigAutoField(
        db_column='RevenueBreakdownID', primary_key=True, serialize=False)
    commodity_code = models.TextField(
        db_column='CommodityCode', max_length=50, null=True, default=None)
    billed_amount = models.DecimalField(
        db_column='BilledAmount', decimal_places=6, max_digits=19, null=True, default=None)
    review_id = models.ForeignKey(
        Review, db_column='ReviewID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.revenue_breakdown_id)

    class Meta:
        verbose_name_plural = 'RevenueBreakdown'
        db_table = 'RevenueBreakdown'


class RevenueBreakdownHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        db_column='VersionNum', default=None)
    is_latest_version = models.BooleanField(
        db_column='IsLatestVersion', default=False)
    updated_on = models.DateTimeField(
        db_column='UpdatedOn', default=None)
    updated_by = models.TextField(
        db_column='UpdatedBy', default=None)
    base_version = models.IntegerField(
        db_column='BaseVersion', default=None)
    comments = models.TextField(
        db_column='Comments', default=None)
    revenue_breakdown_id = models.ForeignKey(
        RevenueBreakdown, db_column='RevenueBreakdownID', on_delete=models.CASCADE, related_name='+')
    revenue_breakdown_version_id = models.BigAutoField(
        db_column='RevenueBreakdownVersionID', primary_key=True, serialize=False)
    commodity_code = models.TextField(
        db_column='CommodityCode', max_length=50, null=True, default=None)
    billed_amount = models.DecimalField(
        db_column='BilledAmount', decimal_places=6, max_digits=19, null=True, default=None)
    review_version_id = models.ForeignKey(
        ReviewHistory, db_column='ReviewVersionID', on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return str(self.revenue_breakdown_version_id)

    class Meta:
        index_together = (("revenue_breakdown_id", "version_num"))
        verbose_name_plural = 'RevenueBreakdown_History'
        db_table = 'RevenueBreakdown_History'


class FreightBillWarning(models.Model):
    freight_bill_warning_id = models.BigAutoField(
        db_column='FreightBillsWarningID', primary_key=True, serialize=False)
    freight_bill_number = models.CharField(
        max_length=50, unique=False, null=True, blank=False, db_column="FreightBillNo")
    origin = models.TextField(
        db_column='Origin', max_length=50, null=True, default=None)
    destination = models.TextField(
        db_column='Destination', max_length=50, null=True, default=None)
    service_level = models.TextField(
        db_column='ServiceLevel', max_length=50, null=True, default=None)
    billed_weight = models.DecimalField(
        db_column='BilledWeight', decimal_places=6, max_digits=19, null=True, default=None)
    costing_date = models.DateField(
        max_length=50, null=True, blank=False, db_column="CostingDate")
    revenue = models.DecimalField(
        db_column='Revenue', decimal_places=6, max_digits=19, null=True, default=None)
    total_cost = models.DecimalField(
        db_column='TotalCost', decimal_places=6, max_digits=19, null=True, default=None)
    profit = models.DecimalField(
        db_column='Profit', decimal_places=6, max_digits=19, null=True, default=None)

    def __str__(self):
        return str(self.freight_bill_warning_id)

    class Meta:
        verbose_name_plural = 'FreightBillWarning'
        db_table = 'FreightBillWarning'


@receiver(models.signals.post_save, sender=AccountTree)
@receiver(models.signals.post_save, sender=Currency)
@receiver(models.signals.post_save, sender=Customer)
@receiver(models.signals.post_save, sender=Language)
@receiver(models.signals.post_save, sender=RequestType)
@receiver(models.signals.post_save, sender=RequestInformation)
@receiver(models.signals.post_save, sender=RequestProfile)
@receiver(models.signals.post_save, sender=Request)
@receiver(models.signals.post_save, sender=Tariff)
@receiver(models.signals.post_save, sender=RequestStatusType)
@receiver(models.signals.post_save, sender=Zone)
@receiver(models.signals.post_save, sender=RequestSection)
@receiver(models.signals.post_save, sender=RateBase)
@receiver(models.signals.post_save, sender=EquipmentType)
@receiver(models.signals.post_save, sender=FreightClass)
@receiver(models.signals.post_save, sender=RequestSectionLane)
@receiver(models.signals.post_save, sender=RequestSectionLanePricingPoint)
@receiver(models.signals.post_save, sender=RequestSectionLanePointType)
@receiver(models.signals.post_save, sender=RequestEditorRight)
def post_save_instance(sender, instance, created, **kwargs):
    from pac.helpers.functions import create_instance_history
    create_instance_history(sender, instance, globals())
