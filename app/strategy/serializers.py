"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe


class StrategySerializer(serializers.ModelSerializer):
    """Serializer for Strategy. Excludes some values which can only be seen with the detailed StrategyDetailedSerializer """
#rest_framework syntax to define class with
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

class StrategyDetailSerializer(StrategySerializer):
    """Serializer for recipe detail view."""

    class Meta(StrategySerializer.Meta):
        fields = StrategySerializer.Meta.fields + ['description']