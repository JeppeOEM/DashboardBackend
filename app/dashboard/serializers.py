"""
Serializers for dashboard API
"""
from rest_framework import serializers
from core.models import (
    Tag,
    Dashboard,
)
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for strategies."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Dashboard
        fields = [
            'id', 'gridConfig', 'tags'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, dashboard):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            #get_or_create jango helper function
            #This is meant to prevent duplicate objects from being created when requests are made in parallel
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            dashboard.tags.add(tag_obj)



    def create(self, validated_data):
        """Create a dashboard."""
        tags = validated_data.pop('tags', [])
        dashboard = Dashboard.objects.create(**validated_data)
        self._get_or_create_tags(tags, dashboard)

        return dashboard

    # def update(self, instance, validated_data):
    #     """Update dashboard."""
    #     tags = validated_data.pop('tags', None)
    #     if tags is not None:
    #         instance.tags.clear()
    #         self._get_or_create_tags(tags, instance)
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance

    def update(self, instance, validated_data):
        """Update dashboard."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class DashboardDetailSerializer(DashboardSerializer):
    """Serializer for dashboard detail view."""
    class Meta(DashboardSerializer.Meta):
        fields = DashboardSerializer.Meta.fields + ['user','description']