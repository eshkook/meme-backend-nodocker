from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('image/', views.getImage),
    path('posts/', views.getPosts)
    
]