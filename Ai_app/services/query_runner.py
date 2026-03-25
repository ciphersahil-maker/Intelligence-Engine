# from django.db import connection

# def run_query(sql):

#     # Fix table name automatically
#     sql = sql.replace("Ai_app_booking", "booking")

#     with connection.cursor() as cursor:
#         cursor.execute(sql)

#         columns = [col[0] for col in cursor.description]
#         rows = cursor.fetchall()

#     data = []

#     for row in rows:
#         data.append(dict(zip(columns, row)))

#     return data


# --------------------------old code-------------------------

from django.db import connection
from decimal import Decimal
from datetime import date, datetime, time




def run_query(sql):

    sql = sql.replace("Ai_app_booking", "booking")

    with connection.cursor() as cursor:
        cursor.execute(sql)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    data = []

    for row in rows:
        clean_row = {}

        for col, val in zip(columns, row):

            if isinstance(val, Decimal):
                val = float(val)

            elif isinstance(val, (date, datetime)):
                val = val.isoformat()

            elif isinstance(val, time):
                val = val.strftime("%H:%M:%S")

            clean_row[col] = val

        data.append(clean_row)

    return data