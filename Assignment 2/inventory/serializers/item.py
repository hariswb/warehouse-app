from rest_framework import serializers
from ..models.item import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['code', 'name', 'unit', 'description', 'stock', 'balance']
        read_only_fields = ['stock', 'balance']
