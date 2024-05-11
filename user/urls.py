"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

app_name = 'user'
# as_view enables reverse() lookups
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
# Django excepts a function for so as_view() to get view function
