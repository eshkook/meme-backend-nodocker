from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import RoomSerializer
import json
import random
import os
from django.conf import settings

def find_dict_by_key_value(dict_list, target_key, target_value):
    for dictionary in dict_list:
        if dictionary.get(target_key) == target_value:
            return dictionary
    return None

# Load data.json once when the module is imported
filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'data.json')
with open(filename, 'r') as file:
    memes_list_of_dicts = json.load(file)

filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
with open(filename, 'r') as file:
    posts_list_of_dicts = json.load(file)   

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

    return Response(posts_list_of_dicts)    

@api_view(['GET'])
def getPost(request, pk):
    post_dict = find_dict_by_key_value(posts_list_of_dicts, id, pk)
    return (Response(post_dict) if post_dict else Response("no such post"))

@api_view(['GET'])
def getUsers(request):

    return Response(users_list_of_dicts)    

@api_view(['GET'])
def getUser(request, pk):
    user_dict = find_dict_by_key_value(users_list_of_dicts, id, pk)
    return (Response(user_dict) if user_dict else Response("no such user"))