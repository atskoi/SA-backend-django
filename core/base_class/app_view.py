import json
import logging
from rest_framework import views, status
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import buildFilterSchema, BulkInsertSchema, BulkUpdateSchema, buildInsertSchema, buildUpdateSchema
from core.base_class.base_app_view import BaseAppView
from jsonschema import validate


# A generic class that can be used for filtering, inserting, updating on models/tables
# request validation and change auditing are implemented automatically
class AppView(BaseAppView):
    GET_ALL_QUERY = """SELECT * FROM dbo.[{self.PRIMARY_TABLE}] ORDER BY {self.PRIMARY_KEY}"""
    GET_SINGLE_QUERY = """SELECT * FROM dbo.[{self.PRIMARY_TABLE}] ORDER BY {self.PRIMARY_KEY} OFFSET 0 ROWS FETCH FIRST 1 ROWS ONLY"""
    GET_FILTERED_QUERY = """{opening_clause} {user_id} {page_clause} {sort_clause} {where_clauses} {closing_clause} """  # filtered query string should have these elements
    COLUMN_MAPPING = {}  # put mapping for sorting and filtering in here
    OPENING_CLAUSE = " "
    CLOSING_CLAUSE = " "

    UPDATE_FIELDS = []  # an array of field names to use when update the record
    INSERT_FIELDS = []  # an array of field names to use when inserting the record
    INSERT_ALL_FIELDS = []  # an array of field names to use when inserting the record after addition derived values are added
    INSERT_PROCEDURE = ''
    INSERT_PROCEDURE_FIELDS = []

    def prepare_get(self, kwargs, request):  # function to call in preparation for running the default GET behavior
        null_op = None

    def prepare_filter(self, data, kwargs):  # optional function to prepare the class or data before filtering
        return data

    def after_filter(self, data, kwargs):  # if additional work is required after the main query, it can be added here
        return data

    def prepare_bulk_update(self, data, kwargs):  # optional function to prepare the class or data before bulk_update
        return data

    def prepare_bulk_insert(self, data, kwargs):  # optional function to prepare the class or data before bulk_insert
        return data

    def after_bulk_insert(self,
                          new_ids):  # after bulk_insert, process the new primary_key_ids and handle any other post-ops
        if self.conn is not None and new_ids is not None and len(new_ids) > 0:
            self.conn.commit()  # default behavior is to commit all changes if there were no errors

    def after_update(self, data, args, kwargs):
        if self.conn is not None:
            self.conn.commit()  # default behavior is to commit all changes if there were no errors

    def delete(self, request, *args, **kwargs):
        try:
            self.user_name = request.user.user_name
            primary_key = self.PRIMARY_KEY.split('.')[-1]
            id = kwargs.get(primary_key)
            # determine what type of delete operation is being requested
            is_active = 0
            is_viewable = 0
            operation = request.GET.get('operation')
            if operation.lower() == 'disable':
                is_active = 0  # inactive but viewable
                is_viewable = 1
            elif operation.lower() == 'enable':
                is_active = 1
                is_viewable = 1
            elif operation.lower() == 'restore':
                is_active = 1
                is_viewable = 1

            set_state = f'''UPDATE dbo.[{self.PRIMARY_TABLE}] SET IsActive = {is_active}, IsInactiveViewable = {is_viewable}
                WHERE {primary_key} = {id}'''
            conn = pyodbc_connection()
            cursor = conn.cursor()
            cursor.execute(set_state)
            self.audit_change(conn, primary_key, id, f'{operation} Row')
            conn.commit()
            return Response({
                "status": "Success",
                "id": id,
                "operation": operation,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'errorMessage': f"The {self.PRIMARY_TABLE} with id {id} could not be deleted",
                'id': id
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        just_column = self.PRIMARY_KEY.split('.')  # get the column name but not the table alias
        just_column = just_column[len(just_column) - 1]
        primary_key_id = kwargs.get(just_column)
        if primary_key_id is not None:
            return self.get_single(primary_key_id, kwargs, request)
        else:
            return self.get_all(request, args, kwargs)

    def get_single(self, primary_key_value, kwargs, request):
        try:
            self.prepare_get(kwargs, request)
            conn = pyodbc_connection()
            cursor = conn.cursor()
            query = self.GET_SINGLE_QUERY.format(primary_key_value=primary_key_value)
            payload = self.process_sql_to_json(cursor, query)
            if payload is not None and len(payload) > 0:
                payload = payload[0]
            else:
                payload = {}
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response({
                'rows': [],
                'count': 0,
                'errorMessage': f"A record could not be found",
                'request': {}
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_all(self, request, args, kwargs):
        try:
            self.prepare_get(kwargs, request)
            conn = pyodbc_connection()
            cursor = conn.cursor()
            query = self.GET_ALL_QUERY
            payload = self.process_sql_to_json(cursor, query)
            return Response(payload, status=status.HTTP_200_OK)
        except:
            return Response({
                'rows': [],
                'count': 0,
                'errorMessage': f"The request for records could not be completed",
                'request': {}
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        requestObj = request.data
        self.user_name = request.user.user_name  # make audit logging info available
        if (requestObj is not None) and (
                requestObj.get('idFilters') is not None or requestObj.get('textFilters') is not None or requestObj.get(
                'textIdFilters') is not None):
            return self.filter_results(requestObj, args, kwargs)  # treat as a filtered request with filters in the body
        else:
            update_result = self.update_records(requestObj, args,
                                                kwargs)  # treat as a bulk update request with one or more rows
            if update_result is None:
                return Response({"status": "Failure", "errorMessage": "Records could not be updated"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"status": "Success", "type": "update", "rowsUpdated": update_result},
                                status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        self.user_name = request.user.user_name  # make audit logging info available
        new_ids = self.bulk_insert(request.data, kwargs)

        if new_ids is None:
            return Response({"status": "Failure", "error": "Records could not be inserted"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif isinstance(new_ids, str):
            return Response({
                'errorMessage': new_ids,
                'request': request.data
            }, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(new_ids, Response):
            return new_ids
        else:
            return Response({"status": "Success", "type": "insert", "ids": new_ids,
                             "message": f"Created {len(new_ids)} new records"},
                            status=status.HTTP_200_OK)

    def bulk_insert(self, requestObj, kwargs):
        # validate the request body matches the bulk update format
        bulk_check = self.fail_validation(requestObj, BulkInsertSchema)
        if bulk_check:
            return bulk_check
        # run any pre-processing specific to the executing class
        insert_rows = self.prepare_bulk_insert(requestObj, kwargs)
        if isinstance(insert_rows, str):
            return insert_rows  # error message passed up
        elif insert_rows is None or len(insert_rows) == 0:
            return "No valid rows found for insertion"
        insert_schema = buildInsertSchema(self.INSERT_FIELDS)
        data_check = self.fail_validation(insert_rows, insert_schema)
        if data_check:
            return data_check
        conn = None

        try:
            new_ids = []
            just_column = self.PRIMARY_KEY.split('.')  # get the column name but not the table alias
            just_column = just_column[len(just_column) - 1]
            if len(insert_rows) > 0:
                if self.conn is not None:  # use an open connection from a current transaction
                    conn = self.conn
                else:
                    conn = pyodbc_connection()  # open a new connection and a transaction

                for row in insert_rows:
                    # Not going to include a dupe-check on PKs. Inserts will fail in SQL causing an exception
                    row = row.get('data')
                    if len(self.INSERT_PROCEDURE) > 0:  # run a stored procedure instead
                        fields = []
                        for col in self.INSERT_FIELDS:
                            colName = col.get('fieldName')
                            colType = col.get('type')
                            if (colName in row.keys()) == False:  # apply a default value if configured
                                if ('default' in col.keys()):
                                    row[colName] = col.get('default')
                            if (colName in row.keys()) == True:
                                # type check the values, and wrap in quotations if they are a string value
                                if row[
                                    colName] is None:  # allow inserting null values; SQL will determine if valid for the column
                                    fields.append("null")
                                elif colType == 'string':
                                    fields.append(f"""'{row[colName]}'""")
                                elif colType == 'number':
                                    fields.append(f"""{row[colName]}""")
                                elif colType == 'boolean':
                                    fields.append(f"{1 if row[colName] == True else 0}")

                        row_proc = self.INSERT_PROCEDURE.format(*fields)
                        cursor = conn.cursor()
                        cursor.execute(row_proc)
                        # get the new pk for audit update. There is no way to reliably guarantee the @@Latest would be the PK we want
                        # so instead we are approximating by grabbing the latest ID added to the primary table which should be
                        # the correct value within this transaction
                        latest_added = 'SELECT top(1) {pk_id} FROM dbo.[{table}] ORDER BY {pk_id} DESC'
                        cursor.execute(latest_added.format(pk_id=just_column, table=self.PRIMARY_TABLE))
                        new_id = cursor.fetchone()[0]
                        new_ids.append(new_id)
                        self.audit_change(conn, just_column, new_id, 'row created')
                    else:
                        # build the base INSERT statement
                        insert_str = f"INSERT INTO dbo.[{self.PRIMARY_TABLE}] "
                        insert_cols = ['IsActive', 'IsInactiveViewable']  # boilerplate values in all tables
                        insert_vals = ['1', '1']
                        # build each assignment statement
                        for col in self.INSERT_FIELDS:
                            # type check the values, and wrap in quotations if they are a string value
                            colName = col.get('fieldName')
                            colType = col.get('type')

                            if (colName in row.keys()) == False:  # apply a default value if configured
                                if ('default' in col.keys()):
                                    row[colName] = col.get('default')
                                elif colType == 'current_datetime':
                                    insert_cols.append(colName)
                                    insert_vals.append(f"CURRENT_TIMESTAMP")
                            if (colName in row.keys()) == True:
                                if row[
                                    colName] is None:  # allow inserting null values; SQL will determine if valid for the column
                                    insert_cols.append(colName)
                                    insert_vals.append("null")
                                elif colType == 'string':
                                    insert_cols.append(colName)
                                    insert_vals.append(f"""'{row[colName]}'""")
                                elif colType == 'number':
                                    insert_cols.append(colName)
                                    insert_vals.append(f"""{row[colName]}""")
                                elif colType == 'boolean':
                                    insert_cols.append(colName)
                                    insert_vals.append(f"{1 if row[colName] == True else 0}")
                        # default columns
                        insert_str += f"""({','.join(insert_cols)}) VALUES ({','.join(insert_vals)})"""
                        # insert this record
                        cursor = conn.cursor()
                        cursor.execute(insert_str)
                        # get the new pk for audit update
                        cursor.execute("SELECT @@IDENTITY AS ID;")
                        new_id = cursor.fetchone()[0]
                        new_ids.append(new_id)
                        self.audit_change(conn, just_column, new_id, 'row created')
                    # commit all changes if not part of a large transaction
                    if self.conn is None:
                        conn.commit()
                    else:  # otherwise, signal the calling class to clean up and commit changes
                        self.after_bulk_insert(new_ids)

                return new_ids
        except Exception as e:
            if conn is not None:
                conn.rollback()
            logging.warning("{} {}".format(type(e).__name__, e.args))

            if e.args[0] == "23000" and "UC_AccessorialOverride" in e.args[1]:
                return "Duplicate detected. Origin/Destination/Section combinations must be unique."
            return None

    # For server-side filtering, the executing class will use all these validation and verification steps
    # SQL injection should be prevented and only valid filter/sort columns should be used
    def filter_results(self, data, args, kwargs):
        print(args, "Args is this")
        print(kwargs, "Kwargs is this")
        print(data, "Data is this")
        requestObj = self.prepare_filter(data, kwargs)
        print(args, "Args is this")
        print(kwargs, "Kwargs is this")
        # get user_id from the session
        user_id = self.request.user.user_id
        if self.schema is None:
            return Response({
                'rows': [], 'count': 0,
                'errorMessage': f"This endpoint does not have a validation schema",
                'request': requestObj
            }, status=status.HTTP_400_BAD_REQUEST)
        # validate request body
        filter_check = self.fail_validation(data, self.schema)
        if filter_check:
            return filter_check
        # retrieve pagination parameters for the query
        page_size = requestObj.get('pageSize')
        page_num = requestObj.get('pageNumber')

        # retrieve sorting parameters for the query
        sortField = requestObj.get('sort').get('sortField').strip()
        sortDirection = requestObj.get('sort').get('sortDirection')
        if sortField in self.COLUMN_MAPPING.keys():
            sortField = self.COLUMN_MAPPING[sortField]['sortColumn']  # get the SQL mapped value
            sortFlip1 = 1 if sortDirection == 'ASC' else 0
            sortFlip2 = 0 if sortDirection == 'ASC' else 1
            sortString = f"ORDER BY CASE WHEN {sortField} IS NULL THEN {sortFlip1} ELSE {sortFlip2} END {sortDirection}, {sortField} {sortDirection}, {self.PRIMARY_KEY} DESC"
        else:  # fail out as this is not a valid column to sort or (or could revert to a default)
            return Response({
                'rows': [],
                'count': 0,
                'errorMessage': f"Not a recognized column to sort on {sortField}",
                'request': requestObj
            }, status=status.HTTP_400_BAD_REQUEST)

        # retrieve filtering parameters for the query
        idFilters = requestObj.get('idFilters')
        textFilters = requestObj.get('textFilters')
        textIdFilters = requestObj.get('textIdFilters')
        where_clauses = ''
        for currentFilter in idFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                flatIds = ','.join([str(i) for i in currentFilter['ids']])
                if len(flatIds) > 0:
                    where_clauses = where_clauses + filterText.format(flatIds)  # [34] to 34
            else:  # fail on invalid column filters
                return Response({
                    'rows': [],
                    'count': 0,
                    'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                    'request': requestObj
                }, status=status.HTTP_400_BAD_REQUEST)
        for currentFilter in textFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                textValue = (currentFilter['filterText']).upper()
                if len(textValue) > 0:
                    where_clauses = where_clauses + filterText.format(textValue)
            else:  # fail on invalid column filters
                return Response({
                    'rows': [],
                    'count': 0,
                    'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                    'request': requestObj
                }, status=status.HTTP_400_BAD_REQUEST)
        for currentFilter in textIdFilters:
            if currentFilter['fieldName'] in self.COLUMN_MAPPING.keys():
                filterText = self.COLUMN_MAPPING[currentFilter['fieldName']]['filter']
                flatIds = '","'.join(currentFilter['ids'])
                if len(flatIds) > 0:  # ignore empty arrays
                    where_clauses = where_clauses + filterText.format(flatIds)  # [34] to 34
            else:  # fail on invalid column filters
                return Response({
                    'rows': [],
                    'count': 0,
                    'errorMessage': f"Not a recognized column to filter on {currentFilter['fieldName']}",
                    'request': requestObj
                }, status=status.HTTP_400_BAD_REQUEST)

        conn = pyodbc_connection()
        cursor = conn.cursor()

        # get the count of rows with the query
        countQuery = self.GET_FILTERED_QUERY.format(
            user_id=user_id,
            opening_clause="SELECT count(1) FROM (",
            page_clause=" ",
            sort_clause=" ",
            where_clauses=where_clauses,
            closing_clause=" ) as counter")
        cursor.execute(countQuery)
        rawCount = cursor.fetchone()
        countValue = rawCount[0]

        # get the requested page of rows
        rowQuery = self.GET_FILTERED_QUERY.format(
            user_id=user_id,
            opening_clause=self.OPENING_CLAUSE,
            page_clause=f" OFFSET {(page_num - 1) * page_size} ROWS FETCH FIRST {page_size} ROWS ONLY",
            sort_clause=sortString,
            where_clauses=where_clauses,
            closing_clause=self.CLOSING_CLAUSE)
        payload = self.process_sql_to_json(cursor, rowQuery)
        processed_payload = self.after_filter(payload, kwargs)
        return Response({
            "rows": processed_payload,
            "totalRows": countValue,
            "request": requestObj
        }, status=status.HTTP_200_OK)

    def update_records(self, data, args, kwargs):
        # validate the request body matches the bulk update format
        bulk_check = self.fail_validation(data, BulkUpdateSchema)

        if bulk_check:
            return bulk_check
        # run any pre-processing specific to the executing class
        data = self.prepare_bulk_update(data, kwargs)
        update_schema = buildUpdateSchema(self.UPDATE_FIELDS)
        data_check = self.fail_validation(data, update_schema)
        if data_check:
            return data_check
        conn = None
        try:
            update_rows = data.get('records')
            update_count = 0
            if len(update_rows) > 0:
                if self.conn is not None:  # use an open connection from a current transaction
                    conn = self.conn
                else:
                    conn = pyodbc_connection()  # open a new connection and a transaction

                for row in update_rows:
                    pk_id = row.get("id")
                    values = row.get('data')

                    # build the base UPDATE statement
                    update_str = f"UPDATE dbo.[{self.PRIMARY_TABLE}] SET "
                    # build each assignment statement
                    for col in self.UPDATE_FIELDS:
                        # type check the values, and wrap in quotations if they are a string value
                        colName = col.get('fieldName')
                        colType = col.get('type')

                        if not (colName in values.keys()):  # apply a default value if configured
                            if ('default' in col.keys()):
                                values[colName] = col.get('default')
                            elif colType == 'current_datetime':
                                update_str += f" {colName} = CURRENT_TIMESTAMP ,"
                        if (colName in values.keys()):
                            if values[
                                colName] is None:  # allow inserting null values; SQL will determine if valid for the column
                                update_str += f" {colName} = null ,"
                            elif colType == 'string':
                                update_str += f""" {colName} = '{values[colName]}' ,"""
                            elif colType == 'number':
                                update_str += f" {colName} = {values[colName]} ,"
                            elif colType == 'boolean':
                                update_str += f" {colName} = {1 if values[colName] == True else 0} ,"

                    update_str = update_str[:-1]  # remove last comma
                    just_column = self.PRIMARY_KEY.split('.')  # get the column name but not the table alias
                    just_column = just_column[len(just_column) - 1]
                    update_str += f" WHERE {just_column} = {pk_id}"
                    # insert this record
                    updated_count = conn.execute(update_str)
                    if hasattr(self, 'SKIP_AUDIT') and not self.SKIP_AUDIT:
                        self.audit_change(conn, just_column, pk_id, 'row values updated')
                    update_count += 1
                # commit all changes if not part of a large transaction
                if self.conn is None:
                    conn.commit()
                else:  # otherwise, signal the calling class to clean up and commit changes
                    self.after_update(data, args, kwargs)

            return update_count
        except Exception as e:
            if conn is not None:
                conn.rollback()
            logging.warning(f"{e}")
            return None
