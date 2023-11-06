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

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from base.models import Profile
from .serializers import ProfileSerializer
from django.db import IntegrityError
from django.contrib.auth import logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

from rest_framework import permissions
from django.contrib import auth
from .serializers import UserSerializer
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator

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
    def get(self, request):
        
        filename = os.path.join(settings.BASE_DIR, 'base', 'api', 'posts.json')
        with open(filename, 'r') as file:
            posts_list_of_dicts = json.load(file)

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

# @api_view(['POST'])
# def signup_view(request):
#     data = request.data
#     username = data.get('username')
#     password = data.get('password')
#     hobbies = data.get('hobbies')
#     age = data.get('age')
#     try:
#         age = int(age)
#         assert 0 <= age <= 120
#     except (ValueError, AssertionError):
#         return Response({'error': 'Invalid age'}, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         user = User.objects.create_user(username=username, password=password)
#     except IntegrityError:
#         return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

#     profile = Profile.objects.create(user=user, hobbies=hobbies, age=age)
#     login(request, user)  # This logs in the user and creates a session

#     return Response({'username': username}, status=status.HTTP_201_CREATED)

# @api_view(['POST'])
# def login_view(request):
#     username = request.data.get('username')
#     password = request.data.get('password')
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return Response({'username': username}, status=status.HTTP_200_OK)
#     else:
#         return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#     logout(request)
#     return Response({"detail": "Logout successful."}, status=200)  

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def get_response_count(request):
#     count = request.data.get('count')
#     return JsonResponse({'count': count+1})

#####################################################################################################################
class CheckAuthenticatedView(APIView):
    def get(self, request, format=None):
        user = self.request.user

        try:
            isAuthenticated = user.is_authenticated

            if isAuthenticated:
                return Response({ 'isAuthenticated': 'success' })
            else:
                return Response({ 'isAuthenticated': 'error' })
        except:
            return Response({ 'error': 'Something went wrong when checking authentication status' })

@method_decorator(csrf_protect, name='dispatch')
class SignupView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        username = data.get('username')
        password = data.get('password')
        hobbies = data.get('hobbies')
        age = data.get('age')

        try:
            if User.objects.filter(username=username).exists():
                return Response({ 'error': 'Username is already taken' }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.create_user(username=username, password=password)
                profile = Profile.objects.create(user=user, hobbies=hobbies, age=age)
                login(request, user)  

                return Response({'username': username}, status=status.HTTP_201_CREATED)
        except:
            return Response({ 'error': 'Something went wrong when registering account' }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data

        username = data['username']
        password = data['password']

        try:
            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return Response({'username': username}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({ 'error': 'Something went wrong when logging in' })

class LogoutView(APIView):
    def post(self, request, format=None):
        try:
            auth.logout(request)
            return Response({"detail": "Logout successful."}, status=200)
        except:
            return Response({ 'error': 'Something went wrong when logging out' }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        return Response({ 'success': 'CSRF cookie set' })

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        user = self.request.user

        try:
            user.delete()  # Directly delete the user object
            return Response({ 'success': 'User deleted successfully' })
        except:
            # It's better to log this error as well
            return Response({ 'error': 'Something went wrong when trying to delete user' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class DeleteAccountView(APIView):
#     def delete(self, request, format=None):
#         user = self.request.user

#         try:
#             User.objects.filter(id=user.id).delete()

#             return Response({ 'success': 'User deleted successfully' })
#         except:
#             return Response({ 'error': 'Something went wrong when trying to delete user' })

class GetResponseView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        count = request.data.get('count')
        return JsonResponse({'count': count+1}) 
      
      