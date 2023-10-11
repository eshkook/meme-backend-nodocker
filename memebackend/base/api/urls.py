from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('image/', views.getImage),
    path('posts/', views.getPosts),
    path('posts/<str:pk>/', views.getPost),
    path('users/', views.getUsers),
    path('users/<str:pk>/', views.getUser)
    
]