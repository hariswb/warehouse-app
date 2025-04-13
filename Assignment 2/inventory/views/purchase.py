from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models.purchase import Purchase, PurchaseDetail
from ..serializers import PurchaseSerializer
from ..models.item import Item
from ..serializers import PurchaseDetailSerializer


class PurchaseListView(APIView):
    def get(self, request):
        purchases = Purchase.objects.filter(is_deleted=False)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseView(APIView):
    def get(self, request, code):
        purchase = get_object_or_404(Purchase, code=code, is_deleted=False)
        serializer = PurchaseSerializer(purchase)
        return Response(serializer.data)

    def put(self, request, code):
        purchase = get_object_or_404(Purchase, code=code, is_deleted=False)
        serializer = PurchaseSerializer(purchase, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):
        purchase = get_object_or_404(Purchase, code=code, is_deleted=False)
        purchase.is_deleted = True
        purchase.save()
        return Response({"message": "Purchase deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class PurchaseDetailListCreateView(APIView):
    def get(self, request, header_code):
        header = get_object_or_404(Purchase, code=header_code, is_deleted=False)
        details = header.details.all()
        serializer = PurchaseDetailSerializer(details, many=True)
        return Response(serializer.data)

    def post(self, request, header_code):
        header = get_object_or_404(Purchase, code=header_code, is_deleted=False)
        data = request.data.copy()
        data['header'] = header.id

        serializer = PurchaseDetailSerializer(data=data)
        if serializer.is_valid():
            detail = serializer.save()

            # Update item's stock and balance
            item = detail.item
            item.stock += detail.quantity
            item.balance += detail.quantity * detail.unit_price
            item.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
