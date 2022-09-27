import importlib
import os
import pyodbc

def pyodbc_connection():
    env = os.getenv("DJANGO_SETTINGS_MODULE")
    if not env:
        from pac.settings.settings import DATABASES
    else:
        DATABASES = importlib.import_module(env).DATABASES

    try:
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                              DATABASES["default"]["HOST"] + ';DATABASE=' + DATABASES["default"]["NAME"] + ';UID=' + DATABASES["default"]["USER"] + ';PWD=' + DATABASES["default"]["PASSWORD"])
    except Exception as e:
        raise e
    return cnxn

def getQueryScalarResult(cursor, query):
        cursor.execute(query)
        cursor_out = cursor.fetchone()
        return cursor_out[0] if cursor_out else None

def getQueryRowResult(cursor, query):
        cursor.execute(query)
        cursor_out = cursor.fetchone()
        row = cursor_out if cursor_out else {}
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))

def getFormattedRowResults(cursor, query):
        cursor.execute(query)
        cursor_out = cursor.fetchall()
        rows = cursor_out if cursor_out else []
        columns = [column[0] for column in cursor.description]
        clean_rows = []
        for row in rows:
            clean_rows.append(dict(zip(columns, row)))
        return clean_rows

def getQueryResults(cursor, query):
        cursor.execute(query)
        cursor_out = cursor.fetchall()
        return cursor_out if cursor_out else []

def executeQuery(cursor, query):
    try:
        cursor.execute(query)
        return 1
    except Exception as e:
        error_msg = e.args[1]
        error_length = len(error_msg)
        head_length = 0
        tail_length = 0
        if error_length > 80:
            head_length = 80
            tail_length = 80
        if head_length > 0:
            print(f'Unable to execute {error_msg[0:head_length]} ... {error_msg[error_length - tail_length: error_length]}')
        else:
            print(f'Unable to execute {error_msg[0:error_length]}')
        return 0