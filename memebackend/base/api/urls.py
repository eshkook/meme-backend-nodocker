from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('image/', views.getImage),
    # path('posts/', views.getPosts, name='get-posts'),
    # path('posts/', views.createPost, name='create-post'),
    path('posts/', views.PostsView.as_view(), name='posts'),
    path('posts/<str:pk>/', views.getPost),
    path('users/', views.getUsers),
    path('users/<str:pk>/', views.getUser),
    path('signup/', views.signup_view),
    path('login/', views.login_view, name='login_view'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/getresponsecount/', views.get_response_count, name='get_response_count')
]