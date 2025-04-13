from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.sell import Sell, SellDetail
from ..models.item import Item
from ..serializers.sell import SellSerializer, SellDetailSerializer


class SellListView(APIView):
    def get(self, request):
        sells = Sell.objects.filter(is_deleted=False)
        serializer = SellSerializer(sells, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SellSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SellView(APIView):
    def get(self, request, code):
        sell = get_object_or_404(Sell, code=code, is_deleted=False)
        serializer = SellSerializer(sell)
        return Response(serializer.data)

    def put(self, request, code):
        sell = get_object_or_404(Sell, code=code, is_deleted=False)
        serializer = SellSerializer(sell, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        sell = get_object_or_404(Sell, code=code, is_deleted=False)
        sell.is_deleted = True
        sell.save()
        return Response({"message": "Sell deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class SellDetailListCreateView(APIView):
    def get(self, request, header_code):
        header = get_object_or_404(Sell, code=header_code, is_deleted=False)
        details = header.details.all()
        serializer = SellDetailSerializer(details, many=True)
        return Response(serializer.data)

    def post(self, request, header_code):
        header = get_object_or_404(Sell, code=header_code, is_deleted=False)
        data = request.data.copy()
        data['header'] = header.id

        serializer = SellDetailSerializer(data=data)
        if serializer.is_valid():
            detail = serializer.save()

            item = detail.item
            quantity = detail.quantity

            if item.stock < quantity:
                return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

            avg_price = item.balance / item.stock if item.stock else 0
            item.stock -= quantity
            item.balance -= quantity * avg_price
            item.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
