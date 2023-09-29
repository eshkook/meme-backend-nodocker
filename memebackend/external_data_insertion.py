import psycopg2

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-1.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

# Establishing the connection
conn = psycopg2.connect(**db_params)

cur = conn.cursor()

# Using a dictionary to store data
data_to_insert = {
    "name": "soccer",
    "description": "only ucl"
}

# SQL statement
sql = """
INSERT INTO base_topic (name, description)
VALUES (%(name)s, %(description)s);
"""

cur.execute(sql, data_to_insert)
conn.commit()

cur.close()
conn.close()