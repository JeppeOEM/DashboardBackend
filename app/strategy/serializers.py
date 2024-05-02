"""
Serializers for strategy APIs
"""
from rest_framework import serializers
from core.models import (
    Strategy,
    Tag,
    Indicator,
    Coin,
    Base
)

class BaseSerializer(serializers.ModelSerializer):
    """Serializer for indicators."""
    class Meta:
        model = Base
        fields = ['id', 'name']
        read_only_fields = ['id']

class CoinSerializer(serializers.ModelSerializer):
    """Serializer for indicators."""
    class Meta:
        model = Coin
        fields = ['id', 'name']
        read_only_fields = ['id']

class IndicatorSerializer(serializers.ModelSerializer):
    """Serializer for indicators."""
    class Meta:
        model = Indicator
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
    indicators = IndicatorSerializer(many=True, required=False)

    class Meta:
        model = Strategy
        fields = [
            'id', 'base', 'coins', 'tags', 'indicators',
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

    def _get_or_create_indicators(self, indicators, strategy):
        """Handle getting or creating indicators as needed."""
        auth_user = self.context['request'].user
        for indicator in indicators:
            indicator_obj, created = Indicator.objects.get_or_create(
                user=auth_user,
                **indicator,
            )
            strategy.indicators.add(indicator_obj)

    def create(self, validated_data):
        """Create a strategy."""
        tags = validated_data.pop('tags', [])
        indicators = validated_data.pop('indicators', [])
        strategy = Strategy.objects.create(**validated_data)
        self._get_or_create_tags(tags, strategy)
        self._get_or_create_indicators(indicators, strategy)

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
        indicators = validated_data.pop('indicators', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if indicators is not None:
            instance.indicators.clear()
            self._get_or_create_indicators(indicators, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class StrategyDetailSerializer(StrategySerializer):
    """Serializer for strategy detail view."""
    class Meta(StrategySerializer.Meta):
        fields = StrategySerializer.Meta.fields + ['description']