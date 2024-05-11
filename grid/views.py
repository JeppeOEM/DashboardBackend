"""
Views for the strategy APIs
"""

from rest_framework import viewsets  # mixins,

from core.models import Grid
from grid import serializers

# from rest_framework.authentication import TokenAuthentication
# from rest_framework.permissions import IsAuthenticated


class GridViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GridSerializer
    queryset = Grid.objects.all()
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    # overwriting get_queryset method

    def get_queryset(self):
        """Retrieve strategies for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
