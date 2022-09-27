import json
import logging
from pac.helpers.connections import pyodbc_connection
from django.db import transaction
import pac.rrf.queries as queries
from rest_framework.response import Response
from rest_framework import status, views, generics
from pac.rrf.serializers import (RequestProfileHistoryRetrieveSerializer,
                                 RequestProfileSerializer, RequestProfileRetrieveSerializer)
from pac.rrf.models import Customer, RequestProfile, RequestProfileHistory, RequestHistory, Request


class RequestProfileView(generics.RetrieveAPIView):
    serializer_class = RequestProfileRetrieveSerializer
    queryset = RequestProfile.objects.filter(is_inactive_viewable=True)
    lookup_field = 'request_id'


class RequestProfileHistory(generics.RetrieveAPIView):
    serializer_class = RequestProfileHistoryRetrieveSerializer
    queryset = RequestProfileHistory.objects.all()
    lookup_field = 'request_id'

    def get_queryset(self):
        return super().get_queryset().filter(
            request_profile_version_id__in=RequestHistory.objects.filter(**self.kwargs).values_list(
                'request_profile_version_id', flat=True))


class RequestProfileUpdate(views.APIView):

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        request_profile = request.data.get("request_profile", {})
        is_macro_save = request.data.get("is_macro_save", False)
        if request_profile:
            request_profile_id = request_profile.get("request_profile_id")
            if not request_profile_id:
                return Response(f"RequestProfile missing primary key: request_profile_id",
                                status=status.HTTP_400_BAD_REQUEST)
            request_profile_instance = RequestProfile.objects.filter(
                request_profile_id=request_profile_id).first()
            if not request_profile_instance:
                return Response(f"RequestProfile object with primary key '{request_profile_id}' does not exist",
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = RequestProfileSerializer(
                request_profile_instance, data=request_profile, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if is_macro_save:
                request_id = request_profile.get("request_id")
                if not request_id:
                    return Response("RequestProfile missing field request_id, can not macro save related Request",
                                    status=status.HTTP_400_BAD_REQUEST)
                request_instance = Request.objects.filter(
                    request_id=request_id).first()
                if not request_instance:
                    return Response(f"Request not found with request_id {request_profile}",
                                    status=status.HTTP_400_BAD_REQUEST)
                request_instance.save()

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response({"status": "Unsuccessful"}, status=status.HTTP_400_BAD_REQUEST)
