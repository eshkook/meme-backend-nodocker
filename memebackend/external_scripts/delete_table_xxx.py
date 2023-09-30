# this can make troubles, try to avoid deleting a table

import psycopg2

db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-2.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

connection = psycopg2.connect(**db_params)
cursor = connection.cursor()

table_name = "base_topic"  # Replace with your table's name

cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
connection.commit()

cursor.close()
connection.close()
