# Using the cursor.execute() method:
# This method allows you to execute raw SQL queries without returning model instances. 
# It's useful when your query doesn't map cleanly onto a model, 
# or when you're performing complex queries involving multiple tables, subqueries, etc.

from django.db import connection

def your_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table1.*, table2.*
            FROM table1
            JOIN table2 ON table1.some_field = table2.some_field
            WHERE table1.another_field = %s
        """, ['some_value'])
        rows = cursor.fetchall()
    # Do something with rows

# Using the raw() method:
# If your JOIN operation maps cleanly onto a model, you can use the raw() method to execute your query and return model instances. 
# However, the raw() method expects your query to return all columns of the model's table, 
# which can be limiting when working with JOIN operations.

from django.db import models

class YourModel(models.Model):
    # Your model fields

def your_view(request):
    raw_query = """
        SELECT your_model.*
        FROM your_model
        JOIN another_model ON your_model.some_field = another_model.some_field
        WHERE your_model.another_field = %s
    """
    params = ['some_value']
    your_model_instances = YourModel.objects.raw(raw_query, params)
    # Do something with your_model_instances
