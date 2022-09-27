import json
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from jsonschema import validate
from core.base_class.base_app_view import BaseAppView

# a generic class for working with Junction tables (that create a many-to-many relationship)
class JunctionView(BaseAppView):
    PRIMARY_COLUMN = '' # the column that will be operated on as a single ID
    SECONDARY_COLUMN = '' # the column that will take an array of IDs

    def set_relations(self, primary_id, secondary_ids, conn):
        # create an string array of the form (xxx, xxx, xxx)
        array_values = f"({','.join([str(i) for i in secondary_ids])})"
        # convert the array into a temp table format that can be selected from
        temp_table = []
        for temp_id in secondary_ids:
            temp_table.append(f'({temp_id})')

        temp_table = ','.join(temp_table)
        # create statements to update all affected rows
        # handle rows that are not in the incoming set of values
        get_ids = """SELECT {primary_key} FROM dbo.[{primary_table}] WHERE {primary_column} = {primary_id}
            AND {secondary_column} NOT IN  {array_values}""".format(
            primary_table = self.PRIMARY_TABLE,
            primary_column = self.PRIMARY_COLUMN,
            primary_id = primary_id,
            secondary_column = self.SECONDARY_COLUMN,
            array_values = array_values,
            primary_key = self.PRIMARY_KEY)
        cursor = conn.cursor()
        cursor.execute(get_ids)
        get_delete_ids = cursor.fetchall()
        update_statement = """UPDATE dbo.[{primary_table}] SET IsActive = 0, IsInactiveViewable = 0
            WHERE {primary_column} = {primary_id} AND {secondary_column} NOT IN {array_values}""".format(
            primary_table = self.PRIMARY_TABLE,
            primary_column = self.PRIMARY_COLUMN,
            primary_id = primary_id,
            secondary_column = self.SECONDARY_COLUMN,
            array_values = array_values)
        cursor.execute(update_statement)
        for delete_row in get_delete_ids:
            self.audit_change(conn, self.PRIMARY_KEY, delete_row[0], 'Record removed')

        # activate any disabled rows that are in the incoming set
        get_ids = """SELECT {primary_key} FROM dbo.[{primary_table}] WHERE {primary_column} = {primary_id}
            AND {secondary_column} IN {array_values} AND (IsActive = 0 OR IsInactiveViewable = 0)""".format(
            primary_table = self.PRIMARY_TABLE,
            primary_column = self.PRIMARY_COLUMN,
            primary_id = primary_id,
            secondary_column = self.SECONDARY_COLUMN,
            array_values = array_values,
            primary_key = self.PRIMARY_KEY)
        cursor.execute(get_ids)
        get_activate_ids = cursor.fetchall()
        update_statement = """UPDATE dbo.[{primary_table}] SET IsActive = 1, IsInactiveViewable = 1
             WHERE {primary_column} = {primary_id} AND {secondary_column} IN  {array_values}
             AND (IsActive = 0 OR IsInactiveViewable = 0)""".format(
             primary_table = self.PRIMARY_TABLE,
             primary_column = self.PRIMARY_COLUMN,
             primary_id = primary_id,
             secondary_column = self.SECONDARY_COLUMN,
             array_values = array_values)
        cursor.execute(update_statement)
        for activate_row in get_activate_ids:
            self.audit_change(conn, self.PRIMARY_KEY, activate_row[0], 'Record activated')

        # insert any un-added rows
        update_statement = """INSERT INTO dbo.[{primary_table}]  (IsActive, IsInactiveViewable, {primary_column}, {secondary_column})
            SELECT 1, 1, {primary_id}, tempID FROM (Values {temp_table}) as TempTable (tempID)
            WHERE tempID NOT IN (SELECT {secondary_column} FROM dbo.[{primary_table}] WHERE {primary_column} = {primary_id})""".format(
            primary_table = self.PRIMARY_TABLE,
            primary_column = self.PRIMARY_COLUMN,
            primary_id = primary_id,
            secondary_column = self.SECONDARY_COLUMN,
            array_values = array_values,
            temp_table = temp_table,
            primary_key = self.PRIMARY_KEY)

        get_ids = """SELECT {primary_key} FROM dbo.[{primary_table}] WHERE {primary_column} = {primary_id}
            AND {secondary_column} NOT IN (SELECT {secondary_column} FROM dbo.[{primary_table}_History]
            WHERE {primary_column} = {primary_id})""".format(
            primary_table = self.PRIMARY_TABLE,
            primary_column = self.PRIMARY_COLUMN,
            primary_id = primary_id,
            secondary_column = self.SECONDARY_COLUMN,
            array_values = array_values,
            temp_table = temp_table,
            primary_key = self.PRIMARY_KEY)
        cursor.execute(get_ids)
        get_new_ids = cursor.fetchall()

        cursor.execute(update_statement)
        for new_row in get_new_ids:
            self.audit_change(conn, self.PRIMARY_KEY, new_row[0], 'Record created')
