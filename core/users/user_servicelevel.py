
from rest_framework.response import Response
from core.base_class.junction_view import JunctionView
import json
import logging

class UserServiceLevelAPI(JunctionView):
    PRIMARY_TABLE = 'UserServiceLevel'
    PRIMARY_KEY = 'UserServiceLevelID'
    PRIMARY_COLUMN = 'UserID'
    SECONDARY_COLUMN = 'ServiceLevelID'