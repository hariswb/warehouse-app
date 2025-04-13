from rest_framework import serializers
from ..models.purchase import Purchase, PurchaseDetail
from ..models.item import Item

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'code', 'date', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PurchaseDetailSerializer(serializers.ModelSerializer):
    item_code = serializers.SlugRelatedField(
        source='item',
        slug_field='code',
        queryset=Item.objects.filter(is_deleted=False)
    )
    header_code = serializers.SlugRelatedField(
        source='header',
        slug_field='code',
        queryset=Purchase.objects.filter(is_deleted=False)
    )

    class Meta:
        model = PurchaseDetail
        fields = ['id', 'item_code', 'quantity', 'unit_price', 'header_code']

