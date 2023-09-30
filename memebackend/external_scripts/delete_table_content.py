import psycopg2

db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-2.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

def delete_all_rows(table_name):
    connection = None
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # SQL to delete all rows from the specified table
        delete_sql = f"DELETE FROM {table_name};"
        
        cursor.execute(delete_sql)
        connection.commit()

        print(f"All rows have been deleted from {table_name}.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection:
            cursor.close()
            connection.close()

table_to_empty = "base_topic"
delete_all_rows(table_to_empty)
