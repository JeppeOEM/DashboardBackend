"""
Views for the strategy APIs
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Dashboard,
    Tag,
)
from dashboard import serializers
#ModelViewSet comes with basic CRUD operations
class DashboardViewSet(viewsets.ModelViewSet):
    """View for manage strategy APIs."""
    # serializer_class = serializers.StrategySerializer
    #### take care of typos here
    serializer_class = serializers.DashboardSerializer
    queryset = Dashboard.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    ####
    #overwriting get_querset method
    def get_queryset(self):
        """Retrieve strategies for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')


    #Overwriting methods from View Class
    #https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    #When we call create on the ViewSet, we can call this method as part of the creation of that new object
    #The Validation Serializer is passed so we are Authenticated and are allowed to create new objects
    def perform_create(self, serializer):
        """Create a new strategy."""

        serializer.save(user=self.request.user)
