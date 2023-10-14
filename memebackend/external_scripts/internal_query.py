from django.db import connection

sql_raw_query = """
        SELECT table1.*, table2.*
        FROM table1
        JOIN table2 
        ON table1.some_field = table2.some_field
        WHERE table1.another_field = some_value
    """

with connection.cursor() as cursor:
    cursor.execute(sql_raw_query)
    rows = cursor.fetchall()

