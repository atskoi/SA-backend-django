import json
import logging
from datetime import datetime
from rest_framework.response import Response
from core.base_class.app_view import AppView
from core.schemas import buildFilterSchema
from pac.helpers.connections import pyodbc_connection

class WeightBreakHeadersAPI(AppView):
  PRIMARY_TABLE = 'WeightBreakHeader'
  PRIMARY_KEY = 'WeightBreakHeaderID'

  COLUMN_MAPPING = {}
  schema = buildFilterSchema(COLUMN_MAPPING)

  UPDATE_FIELDS = [
    {'fieldName': 'IsActive', 'type': 'boolean'},
    {'fieldName': 'IsInactiveViewable', 'type': 'boolean'},
  ]

  def prepare_bulk_update(self, data, kwargs): # optional function to prepare the class or data before bulk_update
    if not hasattr(self, 'conn'):
      self.conn = pyodbc_connection()  # open a new connection and a transaction
    return data
    