import json
import logging
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView

# updating rows of LineHaul Lane Costs
class LaneAPI(AppView):
    PRIMARY_TABLE = 'Lane'
    PRIMARY_KEY = 'l.LaneID'
    COLUMN_MAPPING = { }

    UPDATE_FIELDS = [{'fieldName': 'IsHeadhaul', 'type': 'number'},]
    INSERT_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'OriginTerminalID', 'type': 'number'},
        {'fieldName': 'DestinationTerminalID', 'type': 'number'},
        {'fieldName': 'IsHeadhaul', 'type': 'number'},
    ]


