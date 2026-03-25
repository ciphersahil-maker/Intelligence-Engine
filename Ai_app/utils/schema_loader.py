from django.db import connection


def load_schema():

    schema = ""

    with connection.cursor() as cursor:

        tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """

        cursor.execute(tables_query)

        tables = cursor.fetchall()

        for table in tables:

            table_name = table[0]

            schema += f"\nTable: {table_name}\nColumns:\n"

            column_query = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """

            cursor.execute(column_query)

            columns = cursor.fetchall()

            for col in columns:
                schema += f"- {col[0]}\n"

    return schema