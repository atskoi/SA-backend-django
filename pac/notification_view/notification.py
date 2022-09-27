from pac.helpers.connections import pyodbc_connection, getQueryRowResult
from core.schemas import buildFilterSchema
from core.base_class.app_view import AppView


class NotificationAPI(AppView):
    PRIMARY_TABLE = 'Notification'
    PRIMARY_KEY = 'C.NotificationID'
    GET_ALL_QUERY = """SELECT N.* FROM Notification N
                       INNER JOIN dbo.[User] U ON N.UserID = U.UserID
                       WHERE N.UserID = {user_id} AND N.IsActive = 1
                       ORDER BY N.Timestamp DESC"""
    GET_SINGLE_QUERY = """SELECT * FROM Notification N
                        WHERE N.IsActive = 1 AND N.NotificationID = {notification_id} AND N.UserID = {user_id}                               
                        ORDER BY N.Timestamp DESC"""

    COLUMN_MAPPING = {}
    schema = buildFilterSchema(COLUMN_MAPPING)

    UPDATE_FIELDS = [
        {'fieldName': 'Message', 'type': 'string'},
        {'fieldName': 'IsRead', 'type': 'number'},
        {'fieldName': 'IsNew', 'type': 'number'},
        {'fieldName': 'IsActive', 'type': 'number'},
        {'fieldName': 'IsInactiveViewable', 'type': 'number'},
    ]

    INSERT_FIELDS = [
        {'fieldName': 'Message', 'type': 'string'},
        {'fieldName': 'UserID', 'type': 'number'},
        {'fieldName': 'IsRead', 'type': 'boolean', 'default': 0},
        {'fieldName': 'IsNew', 'type': 'boolean', 'default': 1},
        {'fieldName': 'IsActive', 'type': 'number', 'default': 1},
        {'fieldName': 'IsInactiveViewable', 'type': 'number', 'default': 1},
        {'fieldName': 'Timestamp', 'type': 'current_datetime'},
    ]

    def prepare_get(self, kwargs, request):  # function to call in preparation for running the default GET behavior
      notification_id = kwargs.get("NotificationID", None)
      user = self.request.user
      if user.user_id:
        if notification_id:
            self.GET_SINGLE_QUERY = self.GET_SINGLE_QUERY.format(notification_id=notification_id, user_id=user.user_id)
        else:
            self.GET_ALL_QUERY = self.GET_ALL_QUERY.format(user_id=user.user_id)

    def prepare_bulk_insert(self, data, kwargs):  # optional function to prepare the class or data before bulk_insert
      if not hasattr(self, 'conn') or self.conn is None:
          self.conn = pyodbc_connection()  # open a new connection and a transaction

      cursor = self.conn.cursor()
      user = self.request.user
      for row in data:
          row_data = row['data']
          message = row_data['Message']
          message = message.replace("'", "''")
          row_data['UserID'] = user.user_id
          row_data['Message'] = message
          row['data'] = row_data
      return data

    def prepare_bulk_update(self, data, kwargs):
        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        return data
