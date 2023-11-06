from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('image/', views.getImage),
    path('posts/', views.PostsView.as_view(), name='posts'),
    path('posts/<str:pk>/', views.getPost),
    path('users/', views.getUsers),
    path('users/<str:pk>/', views.getUser),
    # path('signup/', views.signup_view),
    path('signup/', views.SignupView.as_view()),
    # path('login/', views.login_view, name='login_view'),
    path('login/', views.LoginView.as_view()),
    # path('logout/', views.logout_view, name='logout'),
    path('logout/', views.LogoutView.as_view()),
    path('delete/', views.DeleteAccountView.as_view()),
    path('getresponsecount/', views.get_response_count),
    path('getresponsecount/', views.GetResponseView.as_view()),
    path('authenticated/', views.CheckAuthenticatedView.as_view()),
    path('csrf_cookie/', views.GetCSRFToken.as_view())
]