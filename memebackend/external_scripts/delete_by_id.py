import psycopg2

# if you want by uuid instead of id, detect all the id in this code and switch to uuid

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'kkOOK61610216',
    'host': 'database-2.ceor0cxiqb2n.eu-west-1.rds.amazonaws.com',
    'port': '5432'
}

def delete_rows_by_ids(table_name, id_list):
    connection = None
    try:
        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # SQL to delete the rows by their IDs
        delete_sql = f"""
        DELETE FROM {table_name}
        WHERE id = ANY(%s::int[]);
        """

        # Convert list of IDs to a tuple and execute
        cursor.execute(delete_sql, (id_list,))
        connection.commit()

        print(f"{cursor.rowcount} rows have been deleted from {table_name}.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection:
            cursor.close()
            connection.close()

# Use the function
ids_to_delete = [1, 2, 3]
table_name = "base_topic"  
delete_rows_by_ids(table_name, ids_to_delete)
