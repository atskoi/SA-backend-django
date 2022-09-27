from django.db.models import Prefetch
from rest_framework import generics, serializers, status, views
from rest_framework.response import Response

from core.models import Persona, User
from core.serializers import UserRetrieveSerializer, UserUpdateSerializer
from pac.rrf.models import UserServiceLevel, RequestSectionLane, Request, RequestStatusType
from pac.rrf.workflow.workflow import WorkflowManager
from pac.notifications import NotificationManager

from Function_BaseRate_RateWare_Load.utils import RateWareTariffLoader
from rest_framework.permissions import AllowAny
from core.serializers import LoginSerializer, UserSerializer
from django.contrib.auth import login as django_login
from core.base_class.app_view import AppView
from core.schemas import DashboardRequestSchema, buildFilterSchema
import time
import json
import logging
from pac.helpers.connections import pyodbc_connection


class AccountLoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token_str = request.META.get('HTTP_X_CSRFTOKEN', '')
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token_str
        })