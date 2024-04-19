"""
Views for the user API.
"""
from user.serializers import UserSerializer
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics
from rest_framework import generics, authentication, permissions

#CreateApiView handles a post http request designed for creating objects
# It just need to be inherited by a Seiralizer
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    #We need add below to make part of the browseable api ui
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication] #check if has token
    permission_classes = [permissions.IsAuthenticated] # check what permissions the user have

    #gets http objects normally
    #but is overwritten to only get the user
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user