from rest_framework import status, views
import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection, getQueryRowResult, getFormattedRowResults
from pac.rrf.models import (Request, RequestProfile, RequestInformation,
                            RequestSection, RequestSectionLane,
                            RequestSectionLanePricingPoint,
                            AccessorialOverride, AccessorialDetentionOverride, AccessorialStorageOverride)
import pac.rrf.queries as queries
from pac.pre_costing.models import GriReview
from pac.helpers.connections import pyodbc_connection, getFormattedRowResults, getQueryRowResult
from pac.rrf.lanes.lane_sections import LaneSection
from pac.rrf.accessorials.acc_override import AccessorialOverrideAPI, AccessorialDetentionOverrideAPI, \
    AccessorialStorageOverrideAPI
from django.db.models import Q
import pac.rrf.dashboard_queries as dQueries
from core.schemas import DashboardRequestSchema
from core.base_class.app_view import AppView


class CopyRequestTariff(views.APIView):

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.user_id
        data = request.data
        request_type = data.get("RequestType")
        conn = pyodbc_connection()
        cursor = conn.cursor()
        if request_type == 'tender':
            query = queries.GET_REQUEST_LIST.format(user_id, "Tender Tariff")
        elif request_type == 'annual_review':
            query = queries.GET_REQUEST_LIST.format(user_id, "Annual Review Tariff")
        else:
            query = queries.GET_REQUEST_LIST.format(user_id, "Other Tariff")
        payload = getFormattedRowResults(cursor, query)
        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user = self.request.user
            data = request.data

            request_type = data.get("RequestType")
            status_type = data.get("StatusType")
            request_id = data.get("RequestID")
            lang_name = 'English'
            if request_type == 'gri_review':
                gri_batch = GriReview.objects.get(pk=gri_batch_id)

            conn = pyodbc_connection()
            cursor = conn.cursor()

            if (request_type == 'tender' or request_type == 'annual_review' or request_type == 'gri_review') and (status_type == 'updated'):
                query = queries.GET_ACCOUNT_ID.format(request_id)
                account_data = getQueryRowResult(cursor, query)
                account_id = account_data.get('AccountID')
                service_level_id = account_data.get('ServiceLevelID')
                if request_type == 'tender':
                    uni_type = "Tender Tariff"
                elif request_type == 'annual_review':
                    uni_type = "Annual Review Tariff"
                elif request_type == 'gri_review':
                    uni_type = "GRI Review Tariff"
                else:
                    uni_type = "Other Tariff"
                cursor.execute("EXEC [dbo].[Request_By_Account_Select] ?, ?, ?, ?, ?, ?",
                               user.user_id, service_level_id, account_id, None, uni_type, lang_name)
                raw_data = cursor.fetchone()
                cursor.commit()
                payload = json.loads(raw_data[0]) if raw_data[0] else {}
                target_request = Request.objects.filter(request_id=payload["request_id"]).first()
                target_request.request_source_id = request_id
                target_request.save()
                source_request = Request.objects.filter(request_id=request_id).first()
                source_request_profile = getQueryRowResult(cursor,
                                                           f'SELECT * FROM dbo.RequestProfile WHERE RequestID = {request_id}')
                target_request_profile = getFormattedRowResults(cursor,
                                                                f'SELECT * FROM dbo.RequestProfile WHERE RequestID = {payload["request_id"]}')
                for row in target_request_profile:
                    update_profile = {}
                    if row['UsingStandardTariff'] is not None:
                        using_standard_tariff = {'using_standard_tariff': source_request_profile['UsingStandardTariff']}
                        update_profile.update(using_standard_tariff)
                    if row['ExcludeFromFAKRating'] is not None:
                        exclude_from_fak_rating = {
                            'exclude_from_fak_rating': source_request_profile['ExcludeFromFAKRating']}
                        update_profile.update(exclude_from_fak_rating)
                    if row['UseActualWeight'] is not None:
                        use_actual_weight = {'use_actual_weight': source_request_profile['UseActualWeight']}
                        update_profile.update(use_actual_weight)
                    if row['IsClassDensity'] is not None:
                        is_class_density = {'is_class_density': source_request_profile['IsClassDensity']}
                        update_profile.update(is_class_density)
                    if row['AvgWeightedDensity'] is not None:
                        avg_weight_density = {'avg_weight_density': source_request_profile['AvgWeightedDensity']}
                        update_profile.update(avg_weight_density)
                    if row['OverrideDensity'] is not None:
                        override_density = {'override_density': source_request_profile['OverrideDensity']}
                        update_profile.update(override_density)
                    if row['SubjectToCube'] is not None:
                        subject_to_cube = {'subject_to_cube': source_request_profile['SubjectToCube']}
                        update_profile.update(subject_to_cube)
                    if row['LinearLengthRule'] is not None:
                        linear_length_rule = {'linear_length_rule': source_request_profile['LinearLengthRule']}
                        update_profile.update(linear_length_rule)
                    if row['WeightPerLinearLengthRule'] is not None:
                        weight_per_linear_length_rule = {
                            'weight_per_linear_length_rule': source_request_profile['WeightPerLinearLengthRule']}
                        update_profile.update(weight_per_linear_length_rule)
                    if row['AvgWeightedClass'] is not None:
                        avg_weighted_class = {'avg_weighted_class': source_request_profile['AvgWeightedClass']}
                        update_profile.update(avg_weighted_class)
                    if row['OverrideClass'] is not None:
                        override_class = {'override_class': source_request_profile['OverrideClass']}
                        update_profile.update(override_class)
                    if row['FreightElements'] is not None:
                        freight_elements = {'freight_elements': source_request_profile['FreightElements']}
                        update_profile.update(freight_elements)
                    if row['Shipments'] is not None:
                        shipments = {'shipments': source_request_profile['Shipments']}
                        update_profile.update(shipments)
                    if row['ShippingControls'] is not None:
                        shipping_controls = {'shipping_controls': source_request_profile['ShippingControls']}
                        update_profile.update(shipping_controls)
                    if row['Competitors'] is not None:
                        competitors = {'competitors': source_request_profile['Competitors']}
                        update_profile.update(competitors)
                    if row['ClassControls'] is not None:
                        class_controls = {'class_controls': source_request_profile['ClassControls']}
                        update_profile.update(class_controls)
                    update_profile = dict(update_profile)
                    RequestProfile.objects.filter(request_profile_id=row['RequestProfileID']).update(**update_profile)
                source_request_information = getQueryRowResult(cursor,
                                                               f'SELECT * FROM dbo.RequestInformation WHERE RequestID = {request_id}')
                target_request_information = getFormattedRowResults(cursor,
                                                                    f'SELECT * FROM dbo.RequestInformation WHERE RequestID = {payload["request_id"]}')
                for row in target_request_information:
                    update_request_information = {'language': source_request_information['LanguageID'],
                                                  'currency': source_request_information['CurrencyID']}
                    if row['IsNewBusiness'] is not None:
                        is_new_business = {'is_new_business': source_request_information['IsNewBusiness']}
                        update_request_information.update(is_new_business)
                    if row['Priority'] is not None:
                        priority = {'priority': source_request_information['Priority']}
                        update_request_information.update(priority)
                    if row['RequestTypeID'] is not None:
                        request_type = {'request_type': source_request_information['RequestTypeID']}
                        update_request_information.update(request_type)
                    update_request_information = dict(update_request_information)
                    RequestInformation.objects.filter(request_information_id=row['RequestInformationID']).update(
                        **update_request_information)
                try:
                    source_request_section = RequestSection.objects.filter(
                        request_id=source_request.request_id).values_list()
                except RequestSection.DoesNotExist:
                    source_request_section = None
                    if source_request_section is None:
                        return Response(
                            f"RequestSection object with primary key '{source_request_section}' does not exist",
                            status=status.HTTP_400_BAD_REQUEST)
                for idx, row in enumerate(source_request_section):
                    insert_request_section = {'RequestID': target_request.request_id,
                                              'SubServiceLevelID': row[7],
                                              'WeightBreakHeaderID': row[8],
                                              'SectionName': row[9], 'WeightBreak': row[10],
                                              'IsDensityPricing': row[11],
                                              'OverrideDensity': 0 if not row[12] else float(row[12]),
                                              'UnitFactor': float(row[14]),
                                              'MaximumValue': float(row[15]),
                                              'AsRating': row[16], 'HasMin': row[17],
                                              'HasMax': row[18], 'BaseRate': row[19], 'RequestSectionSourceID': row[2]}
                    if row[4] is not None:
                        rate_base = {'RateBaseID': row[4]}
                        insert_request_section.update(rate_base)
                    if row[5] is not None:
                        override_class = {'OverrideClassID': row[5]}
                        insert_request_section.update(override_class)
                    if row[6] is not None:
                        equipment_type = {'EquipmentTypeID': row[6]}
                        insert_request_section.update(equipment_type)
                    if row[13] is not None:
                        commodity = {'CommodityID': row[13]}
                        insert_request_section.update(commodity)
                    post_insert_data = [{"data": insert_request_section}]
                    lane_api = LaneSection()
                    lane_api.conn = conn
                    section = lane_api.bulk_insert(post_insert_data, kwargs=payload["request_id"])
                    source_accessorial_override = AccessorialOverride.objects. \
                        filter(request_section_id=row[2]).values()
                    for idx, override in enumerate(source_accessorial_override):
                        insert_acc_override = {'SubServiceLevelID': override["sub_service_level_id_id"],
                                               'AccHeaderID': override["acc_header_id_id"],
                                               'RequestID': target_request.request_id,
                                               'CarrierMovementType': override["carrier_movement_type"],
                                               'AccRangeTypeID': override["acc_rate_range_field1ID_id"],
                                               'AccRateDock': override["acc_rate_dock"],
                                               'AccRateExcludeLegs': override["acc_rate_exclude_legs"],
                                               'AccRateElevator': override["acc_rate_elevator"],
                                               'AccRateFactorID': override["acc_rate_factor_id_id"],
                                               'AccRateRangeTypeID': override["acc_rate_range_type_id"],
                                               'AccRateStairs': override["acc_rate_stairs"],
                                               'AccRateSurvey': override["acc_rate_survey"],
                                               'AccRateVehicleRestricted': override["acc_rate_vehicle_restricted"],
                                               'AllowBetween': override["allow_between"],
                                               'CommodityID': override["commodity_id_id"],
                                               'DestinationID': override["destination_id"],
                                               'OriginID': override["origin_id"],
                                               'DestinationTypeID': override["destination_type_id_id"],
                                               'OriginTypeID': override["origin_type_id_id"],
                                               'IsWaive': override["is_waive"],
                                               'TMACCOverrideID': override["tmacc_override_id"],
                                               'AccOverrideSourceID': override['acc_override_id'],
                                               'RequestSectionID': section[0]}
                        if override["acc_rate_custom_maximum"] is not None:
                            cust_max = {'AccRateCustomMaximum': override["acc_rate_custom_maximum"]}
                            insert_acc_override.update(cust_max)
                        if override["acc_rate_custom_minimum"] is not None:
                            cust_min = {'AccRateCustomMinimum': override["acc_rate_custom_minimum"]}
                            insert_acc_override.update(cust_min)
                        if override["acc_rate_max_charge"] is not None:
                            rate_max = {'AccRateMaxCharge': override["acc_rate_max_charge"]}
                            insert_acc_override.update(rate_max)
                        if override["acc_rate_min_charge"] is not None:
                            rate_min = {'AccRateMinCharge': override["acc_rate_min_charge"]}
                            insert_acc_override.update(rate_min)
                        if override["min_shipment_value"] is not None:
                            min_shipment = {'MinShipmentValue': override["min_shipment_value"]}
                            insert_acc_override.update(min_shipment)
                        if override["max_shipment_value"] is not None:
                            max_shipment = {'MaxShipmentValue': override["max_shipment_value"]}
                            insert_acc_override.update(max_shipment)
                        if override["min_weight_value"] is not None:
                            min_weight = {'MinWeightValue': override["min_weight_value"]}
                            insert_acc_override.update(min_weight)
                        if override["max_weight_value"] is not None:
                            range_to2 = {'MaxWeightValue': override["max_weight_value"]}
                            insert_acc_override.update(range_to2)
                        if override["acc_rate_shipping_instructionID"] is not None:
                            ship_inst = {'AccRateShippingInstructionID': override["acc_rate_shipping_instructionID"]}
                            insert_acc_override.update(ship_inst)
                        if override["acc_rate_percent"] is not None:
                            rate_pct = {'AccRatePercent': override["acc_rate_percent"]}
                            insert_acc_override.update(rate_pct)
                        if override["usage_percentage"] is not None:
                            usage_pct = {'UsagePercentage': override["usage_percentage"]}
                            insert_acc_override.update(usage_pct)
                        if override["tmid"] is not None:
                            tmid = {'TMID': override["tmid"]}
                            insert_acc_override.update(tmid)
                        insert_acc_override = [{"data": insert_acc_override}]
                        override_api = AccessorialOverrideAPI()
                        override_api.conn = conn
                        override_api.bulk_insert(insert_acc_override, kwargs={'RequestID': target_request.request_id})
                    source_acc_storage_override = AccessorialStorageOverride.objects.filter(
                        request_section_id=row[2]).values()
                    for idx, storage in enumerate(source_acc_storage_override):
                        insert_storage = {'SubServiceLevelID': storage["sub_service_level_id_id"],
                                          'AccHeaderID': storage["acc_header_id_id"],
                                          'RequestID': target_request.request_id, 'BaseRate': storage["base_rate"],
                                          'CurrencyID': storage["currency_id_id"],
                                          'DangerousGoods': storage["dangerous_goods"],
                                          'FreeDays': storage["free_days"],
                                          'HighValue': storage["high_value"],
                                          'IncludeDeliveryDay': storage["include_delivery_day"],
                                          'IncludeTerminalServiceCalendar': storage[
                                              "include_terminal_service_calendar"],
                                          'IsWaive': storage["is_waive"],
                                          'TempControlled': storage["temp_controlled"],
                                          'UnitID': storage["unit_id_id"],
                                          'TMStorageOverrideID': storage["tm_storage_override_id"],
                                          'AccStorageOverrideSourceID': storage["acc_storage_override_id"],
                                          'RequestSectionID': section[0]}
                        if storage["rate_amount"] is not None:
                            rate_amount = {'RateAmount': storage["rate_amount"]}
                            insert_storage.update(rate_amount)
                        if storage["rate_max"] is not None:
                            rate_max = {'RateMax': storage["rate_max"]}
                            insert_storage.update(rate_max)
                        if storage["rate_min"] is not None:
                            rate_min = {'RateMin': storage["rate_min"]}
                            insert_storage.update(rate_min)
                        if storage["rate_per"] is not None:
                            rate_per = {'RatePer': storage["rate_per"]}
                            insert_storage.update(rate_per)
                        if storage["min_std_charge"] is not None:
                            min_std_charge = {'MinStdCharge': storage["min_std_charge"]}
                            insert_storage.update(min_std_charge)
                        if storage["usage_percentage"] is not None:
                            usage_pct = {'UsagePercentage': storage["usage_percentage"]}
                            insert_storage.update(usage_pct)
                        if storage["tmid"] is not None:
                            tmid = {'TMID': storage["tmid"]}
                            insert_storage.update(tmid)
                        insert_storage = [{"data": insert_storage}]
                        storage_api = AccessorialStorageOverrideAPI()
                        storage_api.conn = conn
                        storage_api.bulk_insert(insert_storage, kwargs={'RequestID': target_request.request_id})
                    source_acc_detention_override = AccessorialDetentionOverride.objects.filter(
                        request_section_id=row[2]).values()
                    for idx, detention in enumerate(source_acc_detention_override):
                        insert_detention = {'SubServiceLevelID': detention["sub_service_level_id_id"],
                                            'AccHeaderID': detention["acc_header_id_id"],
                                            'RequestID': target_request.request_id, 'BaseRate': detention["base_rate"],
                                            'CurrencyID': detention["currency_id_id"],
                                            'DestinationID': detention["destination_id"],
                                            'OriginID': detention["origin_id"],
                                            'DestinationTypeID': detention["destination_type_id_id"],
                                            'OriginTypeID': detention["origin_type_id_id"],
                                            'IsWaive': detention["is_waive"],
                                            'TMDetentionOverrideID': detention["tm_detention_override_id"],
                                            'UseActualTime': detention["use_actual_time"],
                                            'AccDetentionOverrideSourceID': detention["acc_detention_override_id"],
                                            'RequestSectionID': section[0]}
                        if detention["exclude_closed_days_detention"] is not None:
                            exclude_detent = {'ExcludeClosedDaysDetention': detention["exclude_closed_days_detention"]}
                            insert_detention.update(exclude_detent)
                        if detention["exclude_closed_days_freetime"] is not None:
                            exclude_free = {'ExcludeClosedDaysFreeTime': detention["exclude_closed_days_freetime"]}
                            insert_detention.update(exclude_free)
                        if detention["start_bill_rate"] is not None:
                            start_bill = {'StartBillRate': detention["start_bill_rate"]}
                            insert_detention.update(start_bill)
                        if detention["usage_percentage"] is not None:
                            usage_pct = {'UsagePercentage': detention["usage_percentage"]}
                            insert_detention.update(usage_pct)
                        if detention["tmid"] is not None:
                            tmid = {'TMID': detention["tmid"]}
                            insert_detention.update(tmid)
                        insert_detention = [{"data": insert_detention}]
                        detention_api = AccessorialDetentionOverrideAPI()
                        detention_api.conn = conn
                        detention_api.bulk_insert(insert_detention, kwargs={'RequestID': target_request.request_id})
                    source_request_section_lane = list(
                        RequestSectionLane.objects.filter(request_section_id=row[2], is_active=True).values_list())
                    for idx, lane in enumerate(source_request_section_lane):
                        cursor.execute(f"SET NOCOUNT ON; DECLARE @NewID BIGINT; EXEC [dbo].[RequestSectionLane_Copy] @SourceRequestSectionLaneID = '{lane[2]}',@DestinationRequestSectionID = '{section[0]}',@UpdatedBy = '{user.user_name}', @CopiedRequestSectionLaneID = @NewID output; SELECT @NewID NewRequestSectionID;")
                        result = cursor.fetchone()
                        cursor.commit()
                        if uni_type == 'GRI Review Tariff':
                            percent_increase = gri_batch.gri_percentage
                            min_gri_dollar_amt = gri_batch.gri_amount

                            lane_commitment = json.loads(lane[12])
                            lane_cost = json.loads(lane[37])

                            for item in [lane_commitment, lane_cost]:
                                for key in item:
                                    new_value = item[key] * (1 + (percent_increase / 100.0))
                                    if new_value < min_gri_dollar_amt:
                                        new_value = min_gri_dollar_amt
                                    item[key] = new_value

                            created_lane = RequestSectionLane.objects.get(pk=result[0])
                            created_lane.cost = lane_cost
                            created_lane.commitment = lane_commitment
                            created_lane.save()

                        payload_result = result[0]
                        source_pricing_point = list(
                            RequestSectionLanePricingPoint.objects.filter(request_section_lane=lane[2],
                                                                          is_active=True).values_list())
                        pricing_points_param_array = []
                        for idx, pricing_point in enumerate(source_pricing_point):
                            req_sect_lane_id = payload_result
                            origin_postal_code_id = pricing_point[4]
                            # destination_postal_code_id = pricing_point[5]
                            flagged = pricing_point[36]
                            pricing_points_param_array.append(
                                [req_sect_lane_id, origin_postal_code_id, destination_postal_code_id,
                                 '{}', '{}', flagged])
                            if len(pricing_points_param_array) > 0:
                                for point in pricing_points_param_array:
                                    table_type = [(point[0], point[1], point[2])]
                                    params = (table_type, "{}", "{}", point[5])
                                    cursor.execute(
                                        "EXEC [dbo].[RequestSectionLanePricingPoint_Insert] @RequestSectionLanePricingPointTableType_Create=?, @UpdatedBy=?, @Comments=?, @Flagged=?",
                                        params)
                                cursor.commit()
                                RequestSectionLanePricingPoint.objects. \
                                    filter(request_section_lane=req_sect_lane_id). \
                                    update(request_section_lane_pricing_point_source_id=lane[2])
                return Response({"status": "Success",
                                 "request_id": target_request.request_id},
                                status=status.HTTP_200_OK)
            else:
                return Response({"status": "Failure",
                                 "error": "The request is not a tender/annual_review type with updated status"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MergeFilteredView(AppView):
    PRIMARY_TABLE = 'dbo.Request'
    PRIMARY_KEY = 'r.RequestID'
    COLUMN_MAPPING = dQueries.ColumnMapping
    schema = DashboardRequestSchema
    GET_FILTERED_QUERY = dQueries.GET_FILTERED_QUERY

    def prepare_filter(self, data, kwargs):
        user_id = self.request.user.user_id
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(
            service_offering_id=service_offering_id,
            type_filter=""" AND R.RequestSourceID IS NOT NULL AND (R.UniType IN ('Other Tariff', 'Tender Tariff', 'Annual Review Tariff') OR R.UniType is NULL) """,
            user_id=user_id
        )
        return data

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.user_id
        data = request.data
        request_id = data.get("RequestID")
        request_type = data.get("RequestType")
        conn = pyodbc_connection()
        cursor = conn.cursor()
        if request_type == 'tender':
            query = queries.GET_REQUEST_LIST.format(user_id, "Tender Tariff")
        elif request_type == 'annual_review':
            query = queries.GET_REQUEST_LIST.format(user_id, "Annual Review Tariff")
        else:
            query = queries.GET_REQUEST_LIST.format(user_id, "Other Tariff")
        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []
        return Response(payload, status=status.HTTP_200_OK)


class MergeRequestTariff(views.APIView):
    def post(self, request):
        try:
            user = self.request.user
            data = request.data
            request_type = data.get("RequestType")
            status_type = data.get("StatusType")
            request_id = data.get("RequestID")

            conn = pyodbc_connection()
            cursor = conn.cursor()

            if (request_type == 'tender' or request_type == 'annual_review') and (status_type == 'updated'):
                # Request that has new added request section/lane becomes source
                source_request = Request.objects.filter(request_id=request_id).first()
                if source_request.request_source_id is None:
                    return Response(
                        f"Request has no RequestSourceID to perform Merge action", status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Request where we want to merge into is target request
                    target_request = Request.objects.filter(request_id=source_request.request_source_id).first()
                    source_request_profile = getQueryRowResult(cursor,
                                                               f'SELECT * FROM dbo.RequestProfile WHERE RequestID = {request_id}')
                    target_request_profile = getFormattedRowResults(cursor,
                                                                    f'SELECT * FROM dbo.RequestProfile WHERE RequestID = {source_request.request_source_id}')
                    for row in target_request_profile:
                        update_profile = {}
                        if row['UsingStandardTariff'] is not None:
                            using_standard_tariff = {
                                'using_standard_tariff': source_request_profile['UsingStandardTariff']}
                            update_profile.update(using_standard_tariff)
                        if row['ExcludeFromFAKRating'] is not None:
                            exclude_from_fak_rating = {
                                'exclude_from_fak_rating': source_request_profile['ExcludeFromFAKRating']}
                            update_profile.update(exclude_from_fak_rating)
                        if row['UseActualWeight'] is not None:
                            use_actual_weight = {'use_actual_weight': source_request_profile['UseActualWeight']}
                            update_profile.update(use_actual_weight)
                        if row['IsClassDensity'] is not None:
                            is_class_density = {'is_class_density': source_request_profile['IsClassDensity']}
                            update_profile.update(is_class_density)
                        if row['AvgWeightedDensity'] is not None:
                            avg_weight_density = {'avg_weight_density': source_request_profile['AvgWeightedDensity']}
                            update_profile.update(avg_weight_density)
                        if row['OverrideDensity'] is not None:
                            override_density = {'override_density': source_request_profile['OverrideDensity']}
                            update_profile.update(override_density)
                        if row['SubjectToCube'] is not None:
                            subject_to_cube = {'subject_to_cube': source_request_profile['SubjectToCube']}
                            update_profile.update(subject_to_cube)
                        if row['LinearLengthRule'] is not None:
                            linear_length_rule = {'linear_length_rule': source_request_profile['LinearLengthRule']}
                            update_profile.update(linear_length_rule)
                        if row['WeightPerLinearLengthRule'] is not None:
                            weight_per_linear_length_rule = {
                                'weight_per_linear_length_rule': source_request_profile['WeightPerLinearLengthRule']}
                            update_profile.update(weight_per_linear_length_rule)
                        if row['AvgWeightedClass'] is not None:
                            avg_weighted_class = {'avg_weighted_class': source_request_profile['AvgWeightedClass']}
                            update_profile.update(avg_weighted_class)
                        if row['OverrideClass'] is not None:
                            override_class = {'override_class': source_request_profile['OverrideClass']}
                            update_profile.update(override_class)
                        if row['FreightElements'] is not None:
                            freight_elements = {'freight_elements': source_request_profile['FreightElements']}
                            update_profile.update(freight_elements)
                        if row['Shipments'] is not None:
                            shipments = {'shipments': source_request_profile['Shipments']}
                            update_profile.update(shipments)
                        if row['ShippingControls'] is not None:
                            shipping_controls = {'shipping_controls': source_request_profile['ShippingControls']}
                            update_profile.update(shipping_controls)
                        if row['Competitors'] is not None:
                            competitors = {'competitors': source_request_profile['Competitors']}
                            update_profile.update(competitors)
                        if row['ClassControls'] is not None:
                            class_controls = {'class_controls': source_request_profile['ClassControls']}
                            update_profile.update(class_controls)
                        update_profile = dict(update_profile)
                        RequestProfile.objects.filter(request_profile_id=row['RequestProfileID']).update(
                            **update_profile)
                    source_request_information = getQueryRowResult(cursor,
                                                                   f'SELECT * FROM dbo.RequestInformation WHERE RequestID = {request_id}')
                    target_request_information = getFormattedRowResults(cursor,
                                                                        f'SELECT * FROM dbo.RequestInformation WHERE RequestID = {source_request.request_source_id}')
                    for info in target_request_information:
                        update_request_information = {'language': source_request_information['LanguageID'],
                                                      'currency': source_request_information['CurrencyID']}
                        if info['IsNewBusiness'] is not None:
                            is_new_business = {'is_new_business': source_request_information['IsNewBusiness']}
                            update_request_information.update(is_new_business)
                        if info['Priority'] is not None:
                            priority = {'priority': source_request_information['Priority']}
                            update_request_information.update(priority)
                        if info['RequestTypeID'] is not None:
                            request_type = {'request_type': source_request_information['RequestTypeID']}
                            update_request_information.update(request_type)
                        update_request_information = dict(update_request_information)
                        RequestInformation.objects.filter(request_information_id=info['RequestInformationID']).update(
                            **update_request_information)
                    target_request_section = RequestSection.objects.filter(
                        request_id=target_request.request_id).values()
                    if len(target_request_section) == 0:
                        return Response(f"Request has no section in the RequestSection table",
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        source_request_section = RequestSection.objects.filter(
                            request_id=source_request.request_id).values_list()
                        for section in source_request_section:
                            # Find request section where the source ID is 0
                            diff_request = RequestSection.objects.filter(
                                (Q(request_section_id=section[2]) &
                                 Q(request_section_source_id=0))).values_list()
                            for request in diff_request:
                                insert_request_section = {'RequestID': target_request.request_id,
                                                          'SubServiceLevelID': request[7],
                                                          'WeightBreakHeaderID': request[8],
                                                          'SectionName': request[9],
                                                          'WeightBreak': request[10],
                                                          'IsDensityPricing': request[11],
                                                          'OverrideDensity': 0 if not request[12] else request[
                                                              12],
                                                          'UnitFactor': float(request[14]),
                                                          'MaximumValue': request[15],
                                                          'AsRating': request[16],
                                                          'HasMin': request[17],
                                                          'HasMax': request[18],
                                                          'BaseRate': request[19],
                                                          'RequestSectionSourceID': 0}
                                if request[4] is not None:
                                    rate_base = {'RateBaseID': request[4]}
                                    insert_request_section.update(rate_base)
                                if request[5] is not None:
                                    override_class = {'OverrideClassID': request[5]}
                                    insert_request_section.update(override_class)
                                if request[6] is not None:
                                    equipment_type = {'EquipmentTypeID': request[6]}
                                    insert_request_section.update(equipment_type)
                                if request[13] is not None:
                                    commodity = {'CommodityID': request[13]}
                                    insert_request_section.update(commodity)
                                post_insert_data = [{"data": insert_request_section}]
                                lane_api = LaneSection()
                                lane_api.conn = conn
                                new_section = lane_api.bulk_insert(post_insert_data,
                                                                   kwargs=source_request.request_id)
                                RequestSection.objects.filter(request_section_id=request[2]). \
                                    update(request_section_source_id=int(new_section[0]))
                            diff_accessorial_override = AccessorialOverride.objects.filter(
                                (Q(request_section_id=section[2]) &
                                 Q(acc_override_source_id=0))).values()
                            for idx, override in enumerate(diff_accessorial_override):
                                insert_acc_override = {'SubServiceLevelID': override["sub_service_level_id_id"],
                                                       'AccHeaderID': override["acc_header_id_id"],
                                                       'RequestID': target_request.request_id,
                                                       'CarrierMovementType': override["carrier_movement_type"],
                                                       'AccRangeTypeID': override["acc_rate_range_field1ID_id"],
                                                       'AccRateDock': override["acc_rate_dock"],
                                                       'AccRateExcludeLegs': override["acc_rate_exclude_legs"],
                                                       'AccRateElevator': override["acc_rate_elevator"],
                                                       'AccRateFactorID': override["acc_rate_factor_id_id"],
                                                       'AccRateRangeTypeID': override["acc_rate_range_type_id"],
                                                       'AccRateStairs': override["acc_rate_stairs"],
                                                       'AccRateSurvey': override["acc_rate_survey"],
                                                       'AccRateVehicleRestricted': override[
                                                           "acc_rate_vehicle_restricted"],
                                                       'AllowBetween': override["allow_between"],
                                                       'CommodityID': override["commodity_id_id"],
                                                       'DestinationID': override["destination_id"],
                                                       'OriginID': override["origin_id"],
                                                       'DestinationTypeID': override["destination_type_id_id"],
                                                       'OriginTypeID': override["origin_type_id_id"],
                                                       'IsWaive': override["is_waive"],
                                                       'TMACCOverrideID': override["tmacc_override_id"],
                                                       'AccOverrideSourceID': override['acc_override_id'],
                                                       'RequestSectionID': section[20]}
                                if override["acc_rate_custom_maximum"] is not None:
                                    cust_max = {'AccRateCustomMaximum': override["acc_rate_custom_maximum"]}
                                    insert_acc_override.update(cust_max)
                                if override["acc_rate_custom_minimum"] is not None:
                                    cust_min = {'AccRateCustomMinimum': override["acc_rate_custom_minimum"]}
                                    insert_acc_override.update(cust_min)
                                if override["acc_rate_max_charge"] is not None:
                                    rate_max = {'AccRateMaxCharge': override["acc_rate_max_charge"]}
                                    insert_acc_override.update(rate_max)
                                if override["acc_rate_min_charge"] is not None:
                                    rate_min = {'AccRateMinCharge': override["acc_rate_min_charge"]}
                                    insert_acc_override.update(rate_min)
                                if override["min_shipment_value"] is not None:
                                    min_shipment = {'MinShipmentValue': override["min_shipment_value"]}
                                    insert_acc_override.update(min_shipment)
                                if override["max_shipment_value"] is not None:
                                    max_shipment = {'MaxShipmentValue': override["max_shipment_value"]}
                                    insert_acc_override.update(max_shipment)
                                if override["min_weight_value"] is not None:
                                    min_weight = {'MinWeightValue': override["min_weight_value"]}
                                    insert_acc_override.update(min_weight)
                                if override["max_weight_value"] is not None:
                                    max_weight = {'MaxWeightValue': override["max_weight_value"]}
                                    insert_acc_override.update(max_weight)
                                if override["acc_rate_shipping_instructionID"] is not None:
                                    ship_inst = {
                                        'AccRateShippingInstructionID': override["acc_rate_shipping_instructionID"]}
                                    insert_acc_override.update(ship_inst)
                                if override["acc_rate_percent"] is not None:
                                    rate_pct = {'AccRatePercent': override["acc_rate_percent"]}
                                    insert_acc_override.update(rate_pct)
                                if override["usage_percentage"] is not None:
                                    usage_pct = {'UsagePercentage': override["usage_percentage"]}
                                    insert_acc_override.update(usage_pct)
                                insert_acc_override = [{"data": insert_acc_override}]
                                override_api = AccessorialOverrideAPI()
                                override_api.conn = conn
                                acc_override = override_api.bulk_insert(insert_acc_override,
                                                                        kwargs={
                                                                            'RequestID': target_request.request_id})
                                AccessorialOverride.objects.filter(acc_override_id=override['acc_override_id']). \
                                    update(acc_override_source_id=acc_override[0])
                            diff_acc_storage_override = AccessorialStorageOverride.objects.filter(
                                (Q(request_section_id=section[2]) & Q(acc_storage_override_source_id=0))).values()
                            for idx, storage in enumerate(diff_acc_storage_override):
                                insert_storage = {'SubServiceLevelID': storage["sub_service_level_id_id"],
                                                  'AccHeaderID': storage["acc_header_id_id"],
                                                  'RequestID': target_request.request_id,
                                                  'BaseRate': storage["base_rate"],
                                                  'CurrencyID': storage["currency_id_id"],
                                                  'DangerousGoods': storage["dangerous_goods"],
                                                  'FreeDays': storage["free_days"],
                                                  'HighValue': storage["high_value"],
                                                  'IncludeDeliveryDay': storage["include_delivery_day"],
                                                  'IncludeTerminalServiceCalendar': storage[
                                                      "include_terminal_service_calendar"],
                                                  'IsWaive': storage["is_waive"],
                                                  'TempControlled': storage["temp_controlled"],
                                                  'UnitID': storage["unit_id_id"],
                                                  'TMStorageOverrideID': storage["tm_storage_override_id"],
                                                  'AccStorageOverrideSourceID': storage["acc_storage_override_id"],
                                                  'RequestSectionID': section[20]}
                                if storage["rate_amount"] is not None:
                                    rate_amount = {'RateAmount': storage["rate_amount"]}
                                    insert_storage.update(rate_amount)
                                if storage["rate_max"] is not None:
                                    rate_max = {'RateMax': storage["rate_max"]}
                                    insert_storage.update(rate_max)
                                if storage["rate_min"] is not None:
                                    rate_min = {'RateMin': storage["rate_min"]}
                                    insert_storage.update(rate_min)
                                if storage["rate_per"] is not None:
                                    rate_per = {'RatePer': storage["rate_per"]}
                                    insert_storage.update(rate_per)
                                if storage["min_std_charge"] is not None:
                                    min_std_charge = {'MinStdCharge': storage["min_std_charge"]}
                                    insert_storage.update(min_std_charge)
                                if storage["usage_percentage"] is not None:
                                    usage_pct = {'UsagePercentage': storage["usage_percentage"]}
                                    insert_storage.update(usage_pct)
                                insert_storage = [{"data": insert_storage}]
                                storage_api = AccessorialStorageOverrideAPI()
                                storage_api.conn = conn
                                acc_storage_override = storage_api.bulk_insert(insert_storage,
                                                                               kwargs={
                                                                                   'RequestID': target_request.request_id})
                                AccessorialStorageOverride.objects.filter(
                                    acc_storage_override_id=storage["acc_storage_override_id"]). \
                                    update(acc_storage_override_source_id=acc_storage_override[0])
                            diff_acc_detention_override = AccessorialDetentionOverride.objects.filter(
                                (Q(request_section_id=section[2]) &
                                 Q(acc_detention_override_source_id=0))).values()
                            for idx, detention in enumerate(diff_acc_detention_override):
                                insert_detention = {'SubServiceLevelID': detention["sub_service_level_id_id"],
                                                    'AccHeaderID': detention["acc_header_id_id"],
                                                    'RequestID': target_request.request_id,
                                                    'BaseRate': detention["base_rate"],
                                                    'CurrencyID': detention["currency_id_id"],
                                                    'DestinationID': detention["destination_id"],
                                                    'OriginID': detention["origin_id"],
                                                    'DestinationTypeID': detention["destination_type_id_id"],
                                                    'OriginTypeID': detention["origin_type_id_id"],
                                                    'IsWaive': detention["is_waive"],
                                                    'TMDetentionOverrideID': detention["tm_detention_override_id"],
                                                    'UseActualTime': detention["use_actual_time"],
                                                    'AccDetentionOverrideSourceID': detention[
                                                        "acc_detention_override_id"],
                                                    'RequestSectionID': section[20]}
                                if detention["exclude_closed_days_detention"] is not None:
                                    exclude_detent = {
                                        'ExcludeClosedDaysDetention': detention["exclude_closed_days_detention"]}
                                    insert_detention.update(exclude_detent)
                                if detention["exclude_closed_days_freetime"] is not None:
                                    exclude_free = {
                                        'ExcludeClosedDaysFreeTime': detention["exclude_closed_days_freetime"]}
                                    insert_detention.update(exclude_free)
                                if detention["start_bill_rate"] is not None:
                                    start_bill = {'StartBillRate': detention["start_bill_rate"]}
                                    insert_detention.update(start_bill)
                                if detention["usage_percentage"] is not None:
                                    usage_pct = {'UsagePercentage': detention["usage_percentage"]}
                                    insert_detention.update(usage_pct)
                                insert_detention = [{"data": insert_detention}]
                                detention_api = AccessorialDetentionOverrideAPI()
                                detention_api.conn = conn
                                acc_detention_override = detention_api.bulk_insert(insert_detention, kwargs={
                                    'RequestID': target_request.request_id})
                                AccessorialDetentionOverride.objects.filter(
                                    acc_detention_override_id=detention["acc_detention_override_id"]). \
                                    update(acc_detention_override_source_id=acc_detention_override[0])
                            source_request_section_lane = list(
                                RequestSectionLane.objects.filter(request_section_id=section[2]).values_list())
                            for lane in source_request_section_lane:
                                diff_source_request_section_lane = list(
                                    RequestSectionLane.objects.filter((Q(request_section_id=section[2]) &
                                                                       Q(request_section_lane_source_id=0))).values_list())
                                if len(diff_source_request_section_lane) > 0:
                                    for diff in diff_source_request_section_lane:
                                        target_req_sect_id = section[24]
                                        orig_type_id = diff[4]
                                        orig_id = diff[5]
                                        dest_type_id = diff[6]
                                        dest_id = diff[7]
                                        is_between = diff[11]
                                        flagged = diff[32]
                                        req_sect_lane_source_id = 0
                                        cursor.execute(
                                            "EXEC [dbo].[RequestSectionLane_Insert] ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                                            target_req_sect_id, orig_type_id, None, orig_id,
                                            dest_type_id, None, dest_id, is_between, flagged,
                                            req_sect_lane_source_id,
                                            None)
                                        result_lane = cursor.fetchone()
                                        cursor.commit()
                                        RequestSectionLane.objects.filter(request_section_lane_id=diff[2]). \
                                            update(request_section_lane_source_id=result_lane[0])
                                diff_source_pricing_point = list(
                                    RequestSectionLanePricingPoint.objects.filter(
                                        (Q(request_section_lane=lane[2]) &
                                         Q(request_section_lane_pricing_point_source_id=None))).values_list())
                                pricing_points_param_array = []
                                if len(diff_source_pricing_point) > 0:
                                    for pricing_point in diff_source_pricing_point:
                                        req_sect_lane_id = lane[33]
                                        origin_postal_code_id = pricing_point[4]
                                        destination_postal_code_id = pricing_point[5]
                                        flagged = pricing_point[36]
                                        pricing_points_param_array.append(
                                            [req_sect_lane_id, origin_postal_code_id,
                                             destination_postal_code_id,
                                             '{}', '{}', flagged])
                                        if len(pricing_points_param_array) > 0:
                                            for point in pricing_points_param_array:
                                                table_type = [(point[0], point[1], point[2])]
                                                params = (table_type, "{}", "{}", point[5])
                                                cursor.execute(
                                                    "EXEC [dbo].[RequestSectionLanePricingPoint_Insert] @RequestSectionLanePricingPointTableType_Create=?, @UpdatedBy=?, @Comments=?, @Flagged=?",
                                                    params)
                                            cursor.commit()
                                            RequestSectionLanePricingPoint.objects.filter(
                                                request_section_lane=lane[2]). \
                                                update(
                                                request_section_lane_pricing_point_source_id=req_sect_lane_id)
                    return Response(f"The request has been successfully merged", status=status.HTTP_200_OK)
            else:
                return Response({"status": "Failure",
                                 "error": "The request is not a tender/annual_review type with updated status"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
