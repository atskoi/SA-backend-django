from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import models
from pac.helpers.connections import pyodbc_connection
import pac.models as pac_models
import pac.rrf.models as pac_rrf_models
import pac.pre_costing.models as pac_pre_costing_models
import pprint


class Command(BaseCommand):
    help = 'Make History'

    def __init__(self):
        super().__init__()
        self.model_map = {'pac_models' : pac_models,
                      'pac_rrf_models': pac_rrf_models,
                      'pac_pre_costing_models' : pac_pre_costing_models}
        self.pp = pprint.PrettyPrinter(indent=4)
        self.warnings = [] # list of errors and warnings to report

    def add_arguments(self, parser):
        parser.add_argument('parent_table', nargs='+', type=str)
        parser.add_argument('--columns', action='store_true', help='A List of tables to audit check')
        parser.add_argument('--class', action='store_true', help='A list of tables to make _History models for - TBD')

    def _get_columns(self, table_name):
        fields_query = """
                        select COLUMN_NAME,DATA_TYPE from INFORMATION_SCHEMA.COLUMNS
                        where TABLE_NAME = '{table_name}'
                        order by COLUMN_NAME;
                        """
        return self._run_query(fields_query.format(table_name=table_name))

    # Find the foreign keys for table_name
    def _get_foreign_keys(self, table_name):
        fk_query = f"""
                    DECLARE @table_name VARCHAR(50) = '{table_name}';
                    select schema_name(fk_tab.schema_id) + '.' + fk_tab.name as foreign_table,
                        fk_col.name as fk_column_name,
                        schema_name(pk_tab.schema_id) + '.' + pk_tab.name as primary_table,
                        pk_col.name as pk_column_name,
                        fk.name as fk_constraint_name
                    from sys.foreign_keys fk
                        inner join sys.tables fk_tab
                            on fk_tab.object_id = fk.parent_object_id
                        inner join sys.tables pk_tab
                            on pk_tab.object_id = fk.referenced_object_id
                        inner join sys.foreign_key_columns fk_cols
                            on fk_cols.constraint_object_id = fk.object_id
                        inner join sys.columns fk_col
                            on fk_col.column_id = fk_cols.parent_column_id
                            and fk_col.object_id = fk_tab.object_id
                        inner join sys.columns pk_col
                            on pk_col.column_id = fk_cols.referenced_column_id
                            and pk_col.object_id = pk_tab.object_id
                    where fk_tab.name = @table_name
                    order by schema_name(fk_tab.schema_id) + '.' + fk_tab.name,
                        schema_name(pk_tab.schema_id) + '.' + pk_tab.name, 
                        fk_cols.constraint_column_id
                """
        return self._run_query(fk_query.format(table_name = table_name))

    # Find the primary key for table_name
    def _get_primary_key(self, table_name):
        primary_key_query = """
            DECLARE @table_name  VARCHAR(50) = '{table_name}';
            SELECT 
                column_name as primary_key
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC 
            
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KCU
                ON TC.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                AND TC.CONSTRAINT_NAME = KCU.CONSTRAINT_NAME 
                AND KCU.table_name=@table_name;        
        """
        data = self._run_query(primary_key_query.format(table_name=table_name))
        return data[0]['primary_key'] if data else ''

    def _make_columns(self, *args, **options):
        print(args, options)
        for pt in options['parent_table']:  # process each table
            self.warnings = []
            print("table to transform is {pt}".format(pt=pt))
            ppk = self._get_primary_key(pt)  # parent primary key
            hpk = self._get_primary_key(pt + '_History')  # history primary key

            # audit metadata columns
            history_exclusions = ['BaseVersion', 'Comments', 'IsActive', 'IsInactiveViewable',
                                  'IsLatestVersion', 'UpdatedBy', 'UpdatedOn', 'VersionNum'] + [hpk]
            parent_exclusions = ['IsActive', 'IsInactiveViewable']

            # get parent and history columns excluding audit metadata columns
            parent_columns = [c['COLUMN_NAME'] for c in self._get_columns(pt)
                              if not c['COLUMN_NAME'] in parent_exclusions]
            history_columns = [c['COLUMN_NAME'] for c in self._get_columns(pt + '_History')
                               if not c['COLUMN_NAME'] in history_exclusions]

            # fail if you cant find parent or history table
            if (not parent_columns):
                print('Parent table not found, aborting...')
                return

            if (not history_columns):
                print('History table not found, aborting...')
                return

            if not (len(parent_columns) == len(history_columns)):
                print('Parent or History tables are missing fields')
                self.warnings.append('Parent or History tables are missing fields')

            # build audit fks from primary table
            AUDIT_FKS = []
            fkeys = []
            for k in self._get_foreign_keys(pt):
                fk_col = k['fk_column_name'].split('.')[-1]  # the foreign key column in parent table
                source_col = k['pk_column_name']  # The source primary key column for the forieign key
                source_table = k['primary_table'].split('.')[-1]  # The source table hosting the source column
                AUDIT_FKS.append(dict(fkCol=fk_col, sourceCol=source_col, sourceTable=source_table,
                                      destCol='', histCol='')  # destCol, histCol default to ''
                                 )
                fkeys.append(fk_col)

            history_fks = {}
            ptfk_exclusions = []
            htfk_exclusions = []
            should_have_version_in_name = []

            # add destCol and histCol from history table
            for htfk in self._get_foreign_keys(pt + '_History'):
                if htfk['fk_column_name'].find('Version') != -1:
                    key = htfk['fk_column_name'].replace('Version', '')
                    history_fks[key] = htfk
                    ptfk_exclusions.append(key)
                    htfk_exclusions.append(htfk['fk_column_name'])
                elif not htfk['fk_column_name'] == ppk:
                    should_have_version_in_name.append(htfk['fk_column_name'])
                    # self.warnings.append('Column {column_name} should have Version in its name'.format(column_name=htfk['fk_column_name']))

            htfk_names = ptfk_exclusions

            for index, afk in enumerate(AUDIT_FKS):
                if afk['fkCol'] in htfk_names:
                    htfk = history_fks.get(afk['fkCol'])
                    dest_col = htfk['fk_column_name'].split('.')[-1]
                    hist_col = htfk['pk_column_name']
                    afk.update(dict(destCol=dest_col, histCol=hist_col))

            # exclude foreign keys from parent and history columns
            history_columns = list(set(history_columns).difference(set(htfk_exclusions)))
            parent_columns = list(set(parent_columns).difference(set(ptfk_exclusions)))
            history_columns.sort()
            parent_columns.sort()

            # self.pp.pprint('parent_columns={parent_columns}\n\n'.format(parent_columns=parent_columns))
            # self.pp.pprint('history_columns={history_columns}\n\n'.format(history_columns=history_columns))

            # build audit columns and values
            AUDIT_COLUMNS = []
            AUDIT_VALUES = []
            for index, col in enumerate(parent_columns):
                AUDIT_COLUMNS.append(col)
                if col in history_columns:
                    AUDIT_VALUES.append(col)
                else:
                    AUDIT_VALUES.append('')

            columns_with_no_audit_values = list(set(AUDIT_COLUMNS).difference(
                list(set(v for v in AUDIT_VALUES if v))
            ))
            history_columns_undefined_in_parent = list(set(history_columns).difference(parent_columns))

            if columns_with_no_audit_values:
                self.warnings.append(
                    'No audit value found for columns {column_names}'.format(
                        column_names=', '.join(columns_with_no_audit_values))
                )

            if history_columns_undefined_in_parent:
                self.warnings.append(
                    'No parent table columns defined for the following history columns {column_names}'.format(
                        column_names=', '.join(history_columns_undefined_in_parent))
                )

            if should_have_version_in_name:
                self.warnings.append(
                    'The following history columns should have Version in their name {column_names}'.format(
                        column_names=', '.join(should_have_version_in_name))
                )

            header = "Here are the columns for table {table}".format(table=pt)
            print('\n\n\n{header}\n{underlines}'.format(header=header, underlines="=" * len(header)))
            print('AUDIT_COLUMNS={audit_columns}\n'.format(audit_columns=AUDIT_COLUMNS))
            print('AUDIT_VALUES={audit_values}\n'.format(audit_values=AUDIT_VALUES))
            print('AUDIT_FKS={audit_fks}'.format(audit_fks=AUDIT_FKS))

            if self.warnings:
                header = "Here are the warnings for table {table}".format(table=pt)
                print('\n\n\n{header}\n{underlines}'.format(header=header, underlines="=" * len(header)))
                for warning in self.warnings:
                    print(warning)
        return

    def _make_class(self, *args, **options):
        pass

    # Find the primary key for table_name
    def _run_query(self, query):
        conn = pyodbc_connection()  # get a connection and start a transaction in case multiple operations are needed
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def handle(self, *args, **options): #main entry point to run the commmand

        if options['class']:
            print("Make History Class")
            self._make_class(*args, **options)
        else:
            print("Make History Columns")
            self._make_columns(*args, **options)