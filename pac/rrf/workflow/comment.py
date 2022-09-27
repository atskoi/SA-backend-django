from pac.helpers.connections import pyodbc_connection, getQueryRowResult
from core.schemas import buildFilterSchema
from core.base_class.app_view import AppView


class CommentAPI(AppView):
    PRIMARY_TABLE = 'Comment'
    PRIMARY_KEY = 'C.CommentID'
    GET_ALL_QUERY = """SELECT C.*, U.UserName FROM Comment C
                       INNER JOIN dbo.[User] U ON C.CreatedBy = U.UserID
                       ORDER BY C.CommentID"""
    GET_SINGLE_QUERY = """SELECT * FROM Comment C
                        WHERE IsActive = 1 AND IsInactiveViewable = 1 AND C.CommentID = {comment_id} AND C.RequestID = {request_id}                               
                        ORDER BY C.CommentID"""

    GET_FILTERED_QUERY = """
        {{opening_clause}}
            SELECT C.Tag,
            C.CommentID,
            C.RequestStatusTypeID,
            C.RequestID,
            C.RequestMajorVersion,
            C.Content,
            C.ParentCommentID,
            C.CreatedOn,
            (Select Count(CommentID) from Comment Re where Re.ParentCommentID = c.CommentID AND Re.RequestID = c.RequestID) as RepliesCount, 
            RS. RequestStatusTypeName, U.UserName FROM [dbo].[Comment] C
            INNER JOIN [dbo].[Request] R ON C.RequestID = R.RequestID
            INNER JOIN dbo.RequestStatusType RS ON C.RequestStatusTypeID = RS.RequestStatusTypeID
            INNER JOIN dbo.[User] U ON C.CreatedBy = U.UserID
            WHERE C.[RequestID] = {request_id} AND C.ParentCommentID = {parent_comment_id}
            {{where_clauses}}
            {{sort_clause}}
            {{page_clause}}
            {{closing_clause}}
        """
    COLUMN_MAPPING = {
        "Tag": {"filterType": "textFilters", "sortColumn": 'C.Tag',
                "filter": " AND C.Tag LIKE '%{0}%' "},
        "CreatedBy": {"filterType": "idFilters", "sortColumn": 'C.CreatedBy',
                      "filter": " AND C.CreatedBy IN ({0}) "},
        "RequestMajorVersion": {"filterType": "idFilters", "sortColumn": 'C.RequestMajorVersion',
                                "filter": " AND C.RequestMajorVersion IN ({0}) "},
        "RequestStatusTypeID": {"filterType": "idFilters", "sortColumn": 'C.RequestStatusTypeID',
                                "filter": " AND C.RequestStatusTypeID IN ({0}) "},
        "CreatedOn": {"sortColumn": "C.CreatedOn", "filter": " "}
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    UPDATE_FIELDS = [
        {'fieldName': 'RequestMajorVersion', 'type': 'number'},
        {'fieldName': 'Tag', 'type': 'string'},
        {'fieldName': 'Content', 'type': 'string'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'ParentCommentID', 'type': 'number'},
        {'fieldName': 'RequestStatusTypeID', 'type': 'number'}]

    INSERT_FIELDS = [
        {'fieldName': 'RequestMajorVersion', 'type': 'number'},
        {'fieldName': 'Tag', 'type': 'string'},
        {'fieldName': 'Content', 'type': 'string'},
        {'fieldName': 'ParentCommentID', 'type': 'number', 'default': 0},
        {'fieldName': 'RequestStatusTypeID', 'type': 'number'},
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'CreatedBy', 'type': 'number'},
        {'fieldName': 'CreatedOn', 'type': 'current_datetime'}]

    def prepare_get(self, kwargs, request):  # function to call in preparation for running the default GET behavior
        comment_id = kwargs.get("CommentID", None)
        request_id = kwargs.get("RequestID", None)
        if comment_id and request_id:
            self.GET_SINGLE_QUERY = self.GET_SINGLE_QUERY.format(comment_id=comment_id, request_id=request_id)

    def prepare_filter(self, data, kwargs):
        request_id = kwargs.get("RequestID", None)
        parent_comment_id = kwargs.get("ParentCommentID", None)
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(request_id=request_id, parent_comment_id=parent_comment_id)
        return data

    def prepare_bulk_insert(self, data, kwargs):  # optional function to prepare the class or data before bulk_insert
        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction

        cursor = self.conn.cursor()
        user = self.request.user
        for row in data:
            row_data = row['data']
            request_id = row_data['RequestID']
            content = row_data['Content']
            content = content.replace("'", "''")
            if request_id is None:
                return []  # cannot complete without RequestID
            request_status = getQueryRowResult(cursor,
                                               f'SELECT * FROM dbo.Request WHERE RequestID = {request_id}')
            row_data['RequestStatusTypeID'] = request_status['RequestStatusTypeID']
            row_data['CreatedBy'] = user.user_id
            row_data['Content'] = content
            row['data'] = row_data
        return data

    def prepare_bulk_update(self, data, kwargs):
        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction

        records = data['records']
        cursor = self.conn.cursor()
        for row in records:
            row_data = row['data']
            request_id = row_data['RequestID']
            if request_id is not None:
                request_status = getQueryRowResult(cursor,
                                                   f'SELECT * FROM dbo.Request WHERE RequestID = {request_id}')
                row_data['RequestStatusTypeID'] = request_status['RequestStatusTypeID']
            row['data'] = row_data
        data['records'] = records
        return data
