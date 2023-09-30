import psycopg2
import pandas as pd

# Sample DataFrame
data = {
    'id': [1, 2, 3],
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

# Prepare the SQL query
insert_sql = """
    INSERT INTO base_topic (id, name, description)
    VALUES (%s, %s, %s)
    ON CONFLICT (id)
    DO UPDATE SET
        name = excluded.name,
        description = excluded.description;
"""

# Iterate over DataFrame rows and execute the SQL
for index, row in df.iterrows():
    cur.execute(insert_sql, (row['id'], row['name'], row['description']))

conn.commit()
cur.close()
conn.close()