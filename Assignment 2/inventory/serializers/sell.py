from rest_framework import serializers
from ..models.sell import Sell, SellDetail
from ..models.item import Item


class SellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell
        fields = ['id', 'code', 'date', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SellDetailSerializer(serializers.ModelSerializer):
    item_code = serializers.SlugRelatedField(
        source='item',
        slug_field='code',
        queryset=Item.objects.filter(is_deleted=False)
    )
    header_code = serializers.SlugRelatedField(
        source='header',
        slug_field='code',
        queryset=Sell.objects.filter(is_deleted=False)
    )

    class Meta:
        model = SellDetail
        fields = ['id', 'item_code', 'quantity', 'header_code']
