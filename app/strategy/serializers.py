"""
Serializers for recipe APIs
"""
from rest_framework import serializers


from core.models import (
    Ingredient,
    Recipe,
    Tag,
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
    """Serializer for Strategy. Excludes some values which can only be seen with the detailed StrategyDetailedSerializer """
#rest_framework syntax to define class with
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
        ]
        read_only_fields = ['id']
        #many=True = we want a list of tags
        tags = TagSerializer(many=True, required=False)

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
    def create(self, validated_data):
        """Create a recipe."""
                #Tags is not part of the Model so pop it first, then use
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

    # def create(self, validated_data):
    #     """Create a recipe."""
    #     tags = validated_data.pop('tags', [])

    #     recipe = Recipe.objects.create(**validated_data)
    #     #Context is passed to serilizer from the view.
    #     auth_user = self.context['request'].user
    #     for tag in tags:
    #         #helper method get_or_create, will not create duplicate tags
    #         tag_obj, created = Tag.objects.get_or_create(
    #             user=auth_user,
    #             **tag, #name=tag['name'] is valid, but **tag is future proofing, if tag will get variables associated with it
    #         )
    #         recipe.tags.add(tag_obj)

    #     return recipe

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)



    #Overwrite create
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class StrategyDetailSerializer(StrategySerializer):
    """Serializer for recipe detail view."""

    class Meta(StrategySerializer.Meta):
        fields = StrategySerializer.Meta.fields + ['description']