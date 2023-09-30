import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

# Sample DataFrame
data = {
    'name': ['Laptop', 'Desktop', 'Tablet'],
    'description': ['High-performance laptop', 'Gaming desktop', 'Lightweight tablet']
}
df = pd.DataFrame(data)

# Define your connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-2.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

# Establishing the connection
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Convert the DataFrame to a list of tuples
tuples = [tuple(x) for x in df.to_numpy()]

# SQL statement for inserting data
insert_sql = "INSERT INTO base_topic (name, description) VALUES %s"

execute_values(cur, insert_sql, tuples)

conn.commit()
cur.close()
conn.close()
