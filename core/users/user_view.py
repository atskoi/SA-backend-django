from django.db.models import Prefetch
from rest_framework import views
from rest_framework.response import Response
from core.models import Persona, User
from rest_framework.permissions import AllowAny
from core.base_class.app_view import AppView
from core.users.user_servicelevel import UserServiceLevelAPI
from core.schemas import DashboardRequestSchema, buildFilterSchema
from pac.helpers.connections import pyodbc_connection
import time
import json
import logging

class UserAPI(AppView):
    PRIMARY_TABLE = 'User'
    PRIMARY_KEY = 'u.UserID'
    COLUMN_MAPPING = {
        "UserName": {"filterType": "textFilters", "sortColumn": 'u.UserName', "filter": " AND u.UserName LIKE '%{0}%' "},
        "ServiceLevels": {"filterType": "idFilters","sortColumn": 'usl.ServiceLevelID', "filter": " AND usl.ServiceLevelID IN ({0}) "},
        "PersonaID": {"filterType": "idFilters","sortColumn": 'u.PersonaID', "filter": " AND u.PersonaID IN ({0}) "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'u.IsActive',
            "filter": """ AND (CASE WHEN u.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN u.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """}
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = """ {opening_clause}
    SELECT u.UserID, u.last_login, u.UserName, u.UserEmail, u.IsActive, u.PersonaID, p.PersonaName,
        u.IsAway, u.HasSelfAssign, u.CanProcessSCS, u.CanProcessRequests, u.CanProcessReviews,
        u.UserManagerID ManagerID, manager.UserName ManagerName,
        CASE WHEN u.IsInactiveViewable = 0 THEN 'Deleted'
            ELSE CASE WHEN u.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
        END AS Status,
        (SELECT usl.ServiceLevelID, sl.ServiceLevelCode, sl.ServiceLevelName
            FROM dbo.UserServiceLevel usl
            INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = usl.ServiceLevelID
            WHERE usl.UserID = u.UserID AND u.PersonaID = 5 AND usl.IsInactiveViewable = 1
            FOR JSON PATH) ServiceLevelString,
        (SELECT uh.UpdatedOn FROM dbo.User_History uh WHERE uh.UserID = u.UserID AND uh.VersionNum = 1) DateAdded,
        (SELECT uh.UpdatedOn FROM dbo.User_History uh WHERE uh.UserID = u.UserID AND uh.IsLatestVersion = 1) UpdatedOn
    FROM dbo.[User] u
    LEFT JOIN dbo.Persona p ON p.PersonaID = u.PersonaID
    LEFT JOIN (SELECT u2.UserID, u2.UserName FROM dbo.[User] u2) manager ON manager.UserID = u.UserManagerID
    LEFT JOIN dbo.UserServiceLevel usl ON usl.UserID = u.UserID
    WHERE 1 = 1 {where_clauses}
    GROUP BY u.UserID, u.last_login, u.UserName, u.UserEmail, u.PersonaID, p.PersonaName,
            u.IsAway, u.HasSelfAssign, u.CanProcessSCS, u.CanProcessRequests, u.CanProcessReviews,
            u.UserManagerID, manager.UserName, u.IsInactiveViewable, u.IsActive
    {sort_clause}
    {page_clause}
    {closing_clause}
    """
    UPDATE_FIELDS = [
        {'fieldName': 'PersonaID', 'type': 'number'},
        {'fieldName': 'IsActive', 'type': 'boolean'},
        {'fieldName': 'HasSelfAssign', 'type': 'boolean'},
#         {'fieldName': 'ManagerID', 'type': 'number'},
        {'fieldName': 'CanProcessRequests', 'type': 'boolean'},
        {'fieldName': 'CanProcessReviews', 'type': 'boolean'},
        {'fieldName': 'CanProcessSCS', 'type': 'boolean'},
        ]
    INSERT_FIELDS = [] # users added through Azure

    def prepare_bulk_update(self, data, kwargs):
        # update UserServiceLevels
        update_rows = data.get('records')
        if len(update_rows) > 0:
            conn = pyodbc_connection() # get a connection and start a transaction
            self.conn = conn
            for row in update_rows:
                values = row.get('data')
                userLevels = values.get('ServiceLevels')
                if userLevels is not None:
                    userServiceLevel = UserServiceLevelAPI()
                    level_ids = []
                    for level in userLevels:
                        level_ids.append(level.get('ServiceLevelID'))
                    userServiceLevel.set_relations(values.get("UserID"), level_ids, conn)
        return data

# separate class just for getting the header info
class UserHeaderView(AppView):
    PRIMARY_TABLE = 'User'
    PRIMARY_KEY = 'u.UserID'

    GET_ALL_QUERY = """
        SELECT
        (SELECT count(1) FROM dbo.[User] ) TotalUsers,
        (SELECT count(1) FROM dbo.[User] WHERE IsActive = 1) ActiveUsers,
        (SELECT count(1) FROM dbo.[User] WHERE IsActive = 0) DisabledUsers,
        (SELECT count(1) FROM dbo.[User] u
            INNER JOIN dbo.User_History uh ON uh.UserID = u.UserID AND uh.IsLatestVersion = 1
            WHERE uh.UpdatedOn > DATEADD(d, -60, GETDATE()) ) NewUsers"""


#     def get(self, request, *args, **kwargs):
#         total_users = User.objects.filter(azure_is_active=True).count()
#         active_users = User.objects.filter(
#             azure_is_active=True, is_active=True).count()
#         inactive_users = User.objects.filter(
#             azure_is_active=True, is_active=False).count()
#         new_users = User.objects.filter(persona__isnull=True).count()
#
#         payload = {
#             "total_users": total_users,
#             "active_users": active_users,
#             "inactive_users": inactive_users,
#             "new_users": new_users
#         }
#
#         return Response(payload, status=status.HTTP_200_OK)