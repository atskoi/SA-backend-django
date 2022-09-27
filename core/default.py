from rest_framework import status, views
from rest_framework.response import Response
import json
import logging

class BackendPing(views.APIView):
    def get (self, request, *args, **kwargs):
        print('Did PING')
        return Response({"status": "pac-new-backend Ping success"}, status=status.HTTP_200_OK)
