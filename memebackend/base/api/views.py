from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .serializers import RoomSerializer
import json
import random
import os
from django.conf import settings

# Load data.json once when the module is imported
filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'data.json')
with open(filename, 'r') as file:
    memes_list_of_dicts = json.load(file)

filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
with open(filename, 'r') as file:
    posts_dict = json.load(file)    

@api_view(['GET']) # the request types that can access this endoint
def getRoutes(request): # this endpoint elaborates what endpoints there are
    routes = [
        'GET /api', # current endpoint
        'GET /api/image', 
    ]
    return Response(routes)

@api_view(['GET'])
def getImage(request):
    # filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'data.json')

    # with open(filename, 'r') as file:
    #     memes_list_of_dicts = json.load(file)

    # random_meme = random.choice(memes_list_of_dicts)['url']

    random_meme = random.choice(memes_list_of_dicts)['url']

    return Response(random_meme)                               


@api_view(['GET'])
def getPosts(request):

    return Response(posts_dict)    