from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.item import Item
from ..serializers import ItemSerializer


class ItemListView(APIView):
    def get(self, request, format=None):
        items = Item.objects.filter(is_deleted=False)
        serializer = ItemSerializer(items, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemView(APIView):
    def get(self, request, code, format=None):
        item = get_object_or_404(Item, code=code, is_deleted=False)
        serializer = ItemSerializer(item)
        return Response(serializer.data) 

    def put(self, request, code):
        item = get_object_or_404(Item, code=code, is_deleted=False)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        item = get_object_or_404(Item, code=code, is_deleted=False)
        item.is_deleted = True
        item.save()
        return Response({"message": "Item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
