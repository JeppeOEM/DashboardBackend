"""
Serializers for dashboard API
"""
from rest_framework import serializers

from core.models import Dashboard


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for strategies."""

    class Meta:
        model = Dashboard
        fields = [
            'id', 'gridConfig', 'description'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a dashboard."""
        # tags = validated_data.pop('tags', [])
        dashboard = Dashboard.objects.create(**validated_data)

        return dashboard

    def update(self, instance, validated_data):
        """Update dashboard."""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
