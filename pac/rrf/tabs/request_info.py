import json
import logging
from pac.helpers.connections import pyodbc_connection
from django.db import transaction
import pac.rrf.queries as queries
from rest_framework.response import Response
from rest_framework import status, views
from pac.rrf.models import Customer, RequestInformation
from pac.rrf.serializers import CustomerSerializer, RequestInformationSerializer

class RequestInfo(views.APIView): # serve the Info tab of a Request
    def get(self, request, *args, **kwargs):
        try:
            request_id = kwargs.get("RequestID")
            version_num = kwargs.get("version_num")
            cnxn = pyodbc_connection()
            cursor = cnxn.cursor()

            if version_num is not None: # get the requested version instead
                # TODO: versioning on Requests not currently functioning as intended
                cursor.execute("EXEC [dbo].[Request_By_ID_Select] ?, ?", request_id, 0)
#                 cursor.execute("EXEC [dbo].[Request_History_By_Number_Select] ?, ?", request_id, version_num)
            else:
                cursor.execute("EXEC [dbo].[Request_By_ID_Select] ?, ?", request_id, 0)
            raw_data = cursor.fetchone()
            payload = json.loads(raw_data[0]) if raw_data[0] else []
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic
    def put(self, request, *args, **kwargs):
        customer = request.data.get("customer", {})

        if customer:
            customer_id = customer.get("customer_id")
            if not customer_id:
                return Response(f"Customer missing primary key: customer_id", status=status.HTTP_400_BAD_REQUEST)
            customer_instance = Customer.objects.filter(
                customer_id=customer["customer_id"]).first()
            if not customer_instance:
                return Response(f"Customer object with primary key '{customer_id}' does not exist",
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = CustomerSerializer(
                customer_instance, data=customer, partial=True)
            serializer.is_valid(raise_exception=True)
            print(f'saving customer {serializer}')
            serializer.save()

        request_information = request.data.get("request_information", {})
        is_macro_save = request.data.get("is_macro_save", False)

        if request_information:
            request_information_id = request_information.get(
                "request_information_id")
            request_id = request_information.get(
                "request_id")
            if not request_information_id and not request_number:
                return Response(f"RequestInformation missing key: request_information_id or request_number",
                                status=status.HTTP_400_BAD_REQUEST)
            if request_information_id:
                request_information_instance = RequestInformation.objects.filter(
                    request_information_id=request_information_id).first()
            else:
                request_information_instance = RequestInformation.objects.filter(
                    request_id=request_id).first()

            if not request_information_instance:
                return Response(f"RequestInformation object with primary key '{request_information_id}' does not exist",
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RequestInformationSerializer(
                request_information_instance, data=request_information, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if is_macro_save:
                request_number = request_information.get("request_number")
                if not request_number:
                    return Response(
                        "RequestInformation missing field request_number, can not macro save related Request",
                        status=status.HTTP_400_BAD_REQUEST)
                request_instance = Request.objects.filter(
                    request_number=request_number).first()
                if not request_instance:
                    return Response(f"Request not found with request_number {request_information}",
                                    status=status.HTTP_400_BAD_REQUEST)
                request_instance.save()

        if not customer and not request_information:
            return Response({"status": "Unsuccessful"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Success"}, status=status.HTTP_200_OK)