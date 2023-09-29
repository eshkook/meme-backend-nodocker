import psycopg2

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-1.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

# Create a connection
conn = psycopg2.connect(**db_params)

# Create a cursor object
cur = conn.cursor()

# Execute a simple query
cur.execute("SELECT * FROM base_profile;")  # Adjust query as needed

# Fetch results
rows = cur.fetchall()
print(len(rows))

# Close the cursor and connection
cur.close()
conn.close()
