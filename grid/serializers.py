"""
Serializers for strategy APIs
"""
from rest_framework import serializers

from core.models import Grid


class GridSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grid
        fields = [
            'id', 'gridConfig', 'description', 'user'
        ]  # Include all fields from the model
        read_only_fields = ['id, user']
