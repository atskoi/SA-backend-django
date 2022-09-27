import json
import logging
import requests
from pac.helpers.connections import pyodbc_connection, getQueryRowResult
from pac.settings.settings import PRICING_ENGINE_URL
from django.db import transaction
from pac.rrf.pricing import PricingEngineView
from rest_framework.response import Response
from rest_framework import status, views
from jsonschema import validate

SPOT_QUOTE_SCHEMA_INTERNAL = {
    "type": "object",
    "properties": {
        "RequestInformation": {
            "type": "object",
            "properties": {
                "CurrencyID": {"type": "number"},
                "ServiceLevel": {"type": "number"}
            }
        },
        "RequestProfile": {
            "type": "object",
            "properties": {
                "UsingStandardTariff": {"type": "number", "enum": [0,1]},
                "AvgWeightedDensity": {"type": "number"},
                "SubjectToCube": {"type": "number"},
                "Shipments": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "OriginServicePoint": {"type": "number"},
                            "Weight": {"type": "number"},
                            "PercentUsage": {"type": "number", "maximum": 100 },
                            "IsLiveLoadPickup": {"type": "number", "enum": [0,1]},
                            "PickupsPerWeek": {"type": "number"},
                            "PickupsPerMonth": {"type": "number"},
                            "Commitment": {"type": "number"},
                        }
                    }
                },
                "FreightElements": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "Description": {"type": "string"},
                            "Length": {"type": "number"},
                            "Width": {"type": "number"},
                            "Height": {"type": "number"},
                            "Weight": {"type": "number"},
                            "PercentUsage": {"type": "number", "maximum": 100}
                        }
                    }
                }
            }
        },
        "RequestSection": {
            "type": "object",
            "properties": {
                "EquipmentType":{"type": "number"},
                "RateBaseID":{"type": "number"},
                "SubServiceLevel":{"type": "number"},
                "WeightBreakHeaderID":{"type": "number"},
                "CommodityID":{"type": "number"}
            }
        },
        "RequestSectionLane": {
            "type": "object",
            "properties": {
                "IsBetween":{"type": "number", "enum": [0,1]},
                "PickupCount":{"type": "number"},
                "DeliveryCount":{"type": "number"},
                "DestinationID":{"type": "number"},
                "DestinationTypeID":{"type": "number", "maximum": 12},
                "OriginID":{"type": "number"},
                "OriginTypeID":{"type": "number", "maximum": 12}
            }
        }
    },
    "required": ["RequestInformation", "RequestProfile", "RequestSection", "RequestSectionLane"]
}

SPOT_QUOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "quotedId": {"type": "number"},
        "orderID": {"type": "string"},
        "billTo": {"type": "string"},
        "customerId": {"type": "string"},
        "originZone": {"type": "string"},
        "destinationZone": {"type": "string"},
        "commodity": {"type": "string"},
        "serviceLevel": {"type": "string"},
        "weight": {"type": "number"},
        "density": {"type": "number"},
        "orderCurrency": {"type": "string"},

        # included but not used values
        "declaredValue": {"type": "number"},
        "numberOfPieces": {"type": "number"},
        "commodities": {"type": "array",
            "items": {"type": "string"}
        },
        "accessorials": {"type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["customerId", "originZone", "destinationZone", "serviceLevel", "weight", "density"]
}

# from External sources, immediately create and price a SpotQuote for a single lane
class SpotQuoteAPI(views.APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_id = self.request.user.user_id
            requestObj = request.data
            # validate the request body against the schema
            try:
                validate(instance=requestObj, schema=SPOT_QUOTE_SCHEMA)
            except Exception as schema_errors:
                msg = f'{schema_errors.message} for {schema_errors.relative_path}'
                return Response({"status": "Failure", "error": msg},
                    status=status.HTTP_400_BAD_REQUEST)

            cnxn = pyodbc_connection()
            cursor = cnxn.cursor()
            customer_id = requestObj.get('customerId', 0)
            account_id = requestObj.get('billTo', '0')
            service_level = requestObj.get('serviceLevel', '')
            # get the account/customer related information or fail if not a recognized customer
            get_customer_info = f"""
                SELECT ssl.SubServiceLevelID, sl.ServiceLevelID, a.AccountID, c.CustomerID
                FROM dbo.Account a
                INNER JOIN dbo.Customer c ON c.AccountID = a.AccountID
                INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = c.ServiceLevelID
                INNER JOIN dbo.SubServiceLevel ssl ON ssl.ServiceLevelID = sl.ServiceLevelID
                WHERE a.AccountNumber = '{account_id}' AND ssl.SubServiceLevelCode = '{service_level}' """
            customer_info = getQueryRowResult(cursor, get_customer_info)
            customer_id = customer_info.get('CustomerID', 0)
            account_id = customer_info.get('AccountID', 0)
            service_level_id = customer_info.get('ServiceLevelID', 0)
            sub_service_level_id = customer_info.get('SubServiceLevelID', 0)
            # TODO: SubjectToCube can also be looked up by customer in a future state
            if customer_info is None or customer_id == 0 or account_id == 0 or service_level_id == 0 or sub_service_level_id == 0:
                return Response({"status": "failure", "SpotQuoteID": -1, "ErrorMessage": "Customer Information could not be found" },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # get the commodity ID, default "dry" equipment type, default WeightBreakID
            commodity_code = requestObj.get('commodity', '')
            get_commodity = f"""SELECT cd.CommodityID, et.EquipmentTypeID, wb.WeightBreakHeaderID
                               FROM dbo.Commodity cd
                               CROSS JOIN dbo.EquipmentType et
                               CROSS JOIN dbo.WeightBreakHeader wb
                               WHERE cd.CommodityCode LIKE '{commodity_code}' AND et.EquipmentTypeCode = 'TF'
                               AND wb.WeightBreakHeaderName = 'Spot Quote Default'"""
            commodity_values = getQueryRowResult(cursor, get_commodity)
            commodity_id = commodity_values.get('CommodityID', 0)
            equipment_id = commodity_values.get('EquipmentTypeID', 0)
            weight_break_id = commodity_values.get('WeightBreakHeaderID')
            if commodity_id == 0 or equipment_id == 0 or weight_break_id == 0:
                return Response({"status": "failure", "SpotQuoteID": -1, "ErrorMessage": "Commodity could not be found" },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # get the origin and destination IDs
            origin_code = requestObj.get('originZone', '')
            dest_code = requestObj.get('destinationZone', '')
            get_locations = f"""SELECT ol.ID OriginPostalCodeID, dl.ID DestinationPostalCode
                                FROM dbo.V_LocationTree ol
                                CROSS JOIN dbo.V_LocationTree dl
                                 where ol.pointTypeID = 7 AND ol.Name LIKE '{origin_code}'
                                 AND  dl.pointTypeID = 7 AND dl.Name LIKE '{dest_code}'"""
            commodity_values = getQueryRowResult(cursor, get_locations)
            origin_id = commodity_values.get('OriginPostalCodeID', 0)
            destination_id = commodity_values.get('DestinationPostalCode', 0)
            if origin_id == 0 or destination_id == 0:
                return Response({"status": "failure", "SpotQuoteID": -1, "ErrorMessage": "Origin or Destination could not be found" },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # build the internal object for creating a Request with a single lane
            currency_id = 1 if requestObj.get('orderCurrency') != 'USD' else 2
            final_obj = {
                      "RequestInformation": {
                          "CurrencyID": currency_id,
                          "ServiceLevel": service_level_id,
                          "CustomerID": customer_id,
                          "CustomerID": account_id,
                      },
                      "RequestProfile": {
                          "UsingStandardTariff": 0,
                          "SubjectToCube": 10,
                          "Shipments": [{
                              "OriginServicePoint":origin_id,
                              "Weight": requestObj.get('weight', 10),
                              "PercentUsage": 100,
                              "IsLiveLoadPickup": 1,
                              "PickupsPerWeek": 1,
                              "PickupsPerMonth": 1,
                              "Commitment": 100
                          }],
                          "FreightElements": [{
                              "Description": "Spot Quote Freight",
                              "Length": 10,
                              "Width": 10,
                              "Height": 10,
                              "Weight": requestObj.get('weight', 10),
                              "PercentUsage": 100
                          }]
                      },
                      "RequestSection": {
                          "EquipmentType": equipment_id,
                          "SubServiceLevel": sub_service_level_id,
                          "WeightBreakHeaderID":weight_break_id,
                          "CommodityID": commodity_id
                      },
                      "RequestSectionLane": {
                          "IsBetween":0,
                          "PickupCount":1,
                          "DeliveryCount":1,
                          "DestinationID":destination_id,
                          "DestinationTypeID":7,
                          "OriginID": origin_id,
                          "OriginTypeID":7
                      }
                  }

            # create the Spot Quote
            create_command = "EXEC [dbo].[Create_SpotQuote] {user_id}, '{data}'".format(user_id=user_id, data=json.dumps(final_obj))
            new_request = getQueryRowResult(cursor, create_command)
            cursor.commit()
            if ('ErrorMessage' in new_request): # could not create the SpotQuote
                return Response({"status": "failure", "SpotQuoteID": -1, "ErrorMessage": new_request['ErrorMessage'] },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # send a REST request to the PricingEngine
            # because we need to include a response, this must a synchronous request and get a responding Cost object
            if ('RequestID' in new_request):
                Pricing = PricingEngineView()
                queue_id = Pricing.add_batch_to_queue(cursor, new_request['RequestID'], user_id,
                    [new_request['RequestSectionLaneID']], 1)
                cursor.commit()
                token_str = request.META.get('HTTP_X_CSRFTOKEN', '')

                # Send the request to PricingEngine immediately
                try:
                    print(f'sending request to pricing? {PRICING_ENGINE_URL}')
                    PRICING_ENGINE_URL2 = 'http://localhost:8001/'
                    token_source = request.META.get('HTTP_FLOW_TYPE')
                    if token_source is not None:
                        token_source = 'access-token' # flag to the pricing engine this is not from a personal authentication
                    engine_response = requests.get(f'{PRICING_ENGINE_URL2}engine/price-lanes/{queue_id}',
                        headers={"X-CSRFToken": token_str, "FLOW-TYPE": token_source}, timeout=2) # 2 second timeout
                    print(f'got back from engine: {engine_response}')
                except Exception as rest_errors:
                    print(f'REST request to Pricing Engine: {rest_errors}')
                    # pricing engine did not respond but continue returning results

                # get the Commitment values
                get_costs = f"""SELECT Cost, Commitment, WorkflowErrors
                    FROM dbo.RequestSectionLane WHERE RequestSectionLaneID = {new_request['RequestID']}"""
                costs = getQueryRowResult(cursor, get_costs)
                # TODO: get returned values from REST request or by looking up in DB?
                cost_values = json.dumps({
                    '0': 10590.6,
                    '1000': 10590.6,
                    '2000': 10590.6,
                    '5000': 10590.6,
                    '10000': 10590.6,
                    '20000': 10590.6
                })
                # mocking out values for now costs['Cost']
                return Response({
                    "status": "success",
                    "SpotQuoteID": new_request['RequestID'],
                    "Costs": json.loads(cost_values)}, status=status.HTTP_200_OK)

            # fall back position
            return Response({"status": "success", "SpotQuoteID": -1, "ErrorMessage": "Spot Quote not created" }, status=status.HTTP_200_OK)

        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "The requested Spot Quote could not be created"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        # check if the SpotQuote has been priced or price-matched
        spot_quote_id = kwargs.get('SpotQuoteID')

        # if completed, return the record, otherwise return that it is still pending
        if 1 == 2:
            payload = {"RequestID": spot_quote_id, "Status": "WIP"}
            return Response(payload, status=status.HTTP_200_OK)
        else:
            return Response({"RequestID": spot_quote_id, "Status": "Pricing not complete"}, status=status.HTTP_200_OK)