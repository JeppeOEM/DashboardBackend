"""
Serializers for recipe APIs
"""
from rest_framework import serializers


from core.models import (
    Recipe,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class StrategySerializer(serializers.ModelSerializer):
    """Serializer for Strategy. Excludes some values which can only be seen with the detailed StrategyDetailedSerializer """
#rest_framework syntax to define class with
    tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']
        #many=True = we want a list of tags
        tags = TagSerializer(many=True, required=False)

    #Overwrite create
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        #Tags is not part of the Model so pop it first, then use
        recipe = Recipe.objects.create(**validated_data)
        #Context is passed to serilizer from the view.
        auth_user = self.context['request'].user
        for tag in tags:
            #helper method get_or_create, will not create duplicate tags
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag, #name=tag['name'] is valid, but **tag is future proofing, if tag will get variables associated with it
            )
            recipe.tags.add(tag_obj)

        return recipe


class StrategyDetailSerializer(StrategySerializer):
    """Serializer for recipe detail view."""

    class Meta(StrategySerializer.Meta):
        fields = StrategySerializer.Meta.fields + ['description']