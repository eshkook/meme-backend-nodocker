from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import RoomSerializer
import json
import random
import os
from django.conf import settings

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework import status

def find_dict_by_key_value(dict_list, target_key, target_value):
    for dictionary in dict_list:
        if dictionary.get(target_key) == target_value:
            return dictionary
    return None

# Load data.json once when the module is imported
filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'data.json')
with open(filename, 'r') as file:
    memes_list_of_dicts = json.load(file)

# filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
# with open(filename, 'r') as file:
#     posts_list_of_dicts = json.load(file)   

filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'users.json')
with open(filename, 'r') as file:
    users_list_of_dicts = json.load(file)       

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
def getPosts(request):

    filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
    with open(filename, 'r') as file:
        posts_list_of_dicts = json.load(file)

    return Response(posts_list_of_dicts)    

@api_view(['GET'])
def getPost(request, pk):

    filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
    with open(filename, 'r') as file:
        posts_list_of_dicts = json.load(file)

    post_dict = find_dict_by_key_value(posts_list_of_dicts, id, pk)
    return (Response(post_dict) if post_dict else Response("no such post"))

@api_view(['POST'])
@parser_classes([JSONParser])  # Specify JSON parser for parsing POST request data
def createPost(request):
    new_post = request.data  # Get data from POST request

    filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
    with open(filename, 'r') as file:  # Open file in read mode to get existing posts
        posts_list_of_dicts = json.load(file)

    # Handle missing/empty title and body
    title = new_post.get('title', '')
    body = new_post.get('body', '')
    if not title and not body:
        return Response({'error': 'Both title and body cannot be missing or empty'}, status=status.HTTP_400_BAD_REQUEST)

    # Handle missing id
    existing_ids = [int(post['id']) for post in posts_list_of_dicts]
    generated_id = str(max(existing_ids) + 1) if existing_ids else '1'
    post_id = new_post.get('id', generated_id)

    # Construct the new post object
    new_post = {
        'id': post_id,
        'title': title,
        'body': body
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
    user_dict = find_dict_by_key_value(users_list_of_dicts, id, pk)
    return (Response(user_dict) if user_dict else Response("no such user"))