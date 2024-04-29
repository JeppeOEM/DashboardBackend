"""
Serializers for strategy APIs
"""
from rest_framework import serializers
from core.models import (
    Strategy,
    Tag,
    Ingredient,
)
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']
class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
class StrategySerializer(serializers.ModelSerializer):
    """Serializer for strategies."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Strategy
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, strategy):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            strategy.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, strategy):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            strategy.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a strategy."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        strategy = Strategy.objects.create(**validated_data)
        self._get_or_create_tags(tags, strategy)
        self._get_or_create_ingredients(ingredients, strategy)

        return strategy

    # def update(self, instance, validated_data):
    #     """Update strategy."""
    #     tags = validated_data.pop('tags', None)
    #     if tags is not None:
    #         instance.tags.clear()
    #         self._get_or_create_tags(tags, instance)
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance

    def update(self, instance, validated_data):
        """Update strategy."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class StrategyDetailSerializer(StrategySerializer):
    """Serializer for strategy detail view."""
    class Meta(StrategySerializer.Meta):
        fields = StrategySerializer.Meta.fields + ['description']