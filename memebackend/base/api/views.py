from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import RoomSerializer
import json
import random
import os
from django.conf import settings

from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework import status

from rest_framework.views import APIView

from rest_framework.pagination import PageNumberPagination

def find_dict_by_key_value(dict_list, target_key, target_value):
    for dictionary in dict_list:
        if dictionary.get(target_key) == target_value:
            return dictionary
    return None

# Load data.json once when the module is imported
filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'data.json')
with open(filename, 'r') as file:
    memes_list_of_dicts = json.load(file)  

filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'users.json')
with open(filename, 'r') as file:
    users_list_of_dicts = json.load(file)  

# Define a custom paginator class
class CustomPagination(PageNumberPagination):
    page_size = 2  # Set a default page size
    page_size_query_param = '_limit'  # Allow the client to override the page size with a query parameter         

@api_view(['GET']) # the request types that can access this endoint
def getRoutes(request): # this endpoint elaborates what endpoints there are
    routes = [
        'GET /api', # current endpoint
        'GET /api/image',
        'GET /api/posts',  
        'GET /api/posts/:id',
        'GET /api/users',  
        'GET /api/users/:id',
    ]
    return Response(routes)

@api_view(['GET'])
def getImage(request):

    random_meme = random.choice(memes_list_of_dicts)['url']

    return Response(random_meme)                               

@api_view(['GET'])
def getPost(request, pk):
    try:
        pk = int(pk)  # Ensure pk is an integer
    except ValueError:
        return Response({"detail": "Invalid post ID"}, status=400)  # Return a 400 Bad Request error if pk is not a valid integer

    filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
    with open(filename, 'r') as file:
        posts_list_of_dicts = json.load(file)
    
    post_dict = find_dict_by_key_value(posts_list_of_dicts, "id", pk)
    if post_dict:
        return Response(post_dict)
    else:
        return Response({"detail": "no such post"}, status=404)

class PostsView(APIView):
    # def get(self, request):
        
    #     filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
    #     with open(filename, 'r') as file:
    #         posts_list_of_dicts = json.load(file)

    #     return Response(posts_list_of_dicts)

    def get(self, request):
        filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
        with open(filename, 'r') as file:
            posts_list_of_dicts = json.load(file)

        # Check for pagination parameters
        page_param = request.query_params.get('_page')
        limit_param = request.query_params.get('_limit')
        sort_param = request.query_params.get('_sort')

        if page_param and limit_param:
            paginator = CustomPagination()
            paginator.page_size = int(limit_param)  # Override the page size if _limit is provided
            paginated_posts = paginator.paginate_queryset(posts_list_of_dicts, request)
            # Optionally sort the paginated posts if _sort is provided
            if sort_param:
                paginated_posts = sorted(paginated_posts, key=lambda x: x.get(sort_param))
            return paginator.get_paginated_response(paginated_posts)
        else:
            # Optionally sort all posts if _sort is provided
            if sort_param:
                posts_list_of_dicts = sorted(posts_list_of_dicts, key=lambda x: x.get(sort_param))
            return Response(posts_list_of_dicts)
     
    def post(self, request):

        new_post = request.data  # Get data from POST request

        # Validate userId
        userId = new_post.get('userId')
        if userId is None:
            return Response({'error': 'userId is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            userId = int(userId)  # Ensure userId is an integer
        except ValueError:
            return Response({'error': 'userId must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if userId exists
        user_exists = find_dict_by_key_value(users_list_of_dicts, 'id', userId)
        if not user_exists:
            return Response({'error': 'No such user'}, status=status.HTTP_400_BAD_REQUEST)

        filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
        with open(filename, 'r') as file:  # Open file in read mode to get existing posts
            posts_list_of_dicts = json.load(file)

        # Handle missing/empty title and body
        title = new_post.get('title', '')
        body = new_post.get('body', '')
        if not title and not body:
            return Response({'error': 'Both title and body cannot be missing or empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new post id
        existing_ids = [int(post['id']) for post in posts_list_of_dicts]
        # generated_id = str(max(existing_ids) + 1) if existing_ids else '1'
        generated_id = max(existing_ids) + 1 if existing_ids else 1

        # Construct the new post object
        new_post = {
            'id': generated_id,
            'title': title,
            'body': body,
            'userId': userId  # Include userId in the new post object
        }

        # Append the new post to the list and update the file
        posts_list_of_dicts.append(new_post)
        with open(filename, 'w') as file:  # Open file in write mode to update posts
            json.dump(posts_list_of_dicts, file, indent=4)  # Write updated data back to file

        return Response(new_post, status=status.HTTP_201_CREATED)  # Return new post with 201 Created status

@api_view(['GET'])
def getUsers(request):

    return Response(users_list_of_dicts)    

@api_view(['GET'])
def getUser(request, pk):
    try:
        pk = int(pk)  # Convert pk to integer
    except ValueError:
        return Response({"detail": "Invalid user ID"}, status=400)  # Return 400 Bad Request for invalid IDs
    
    user_dict = find_dict_by_key_value(users_list_of_dicts, "id", pk)
    if user_dict:
        return Response(user_dict)
    else:
        return Response({"detail": "no such user"}, status=404)
