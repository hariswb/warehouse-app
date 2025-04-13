from django.urls import include, path
from rest_framework import routers

from .views.item import ItemListView, ItemView
from .views.purchase import PurchaseListView, PurchaseView, PurchaseDetailListCreateView
from .views.sell import SellListView, SellView, SellDetailListCreateView
from .views.stock_report import StockReportView

urlpatterns = [
    path('items/', ItemListView.as_view()),
    path('items/', ItemView.as_view()), 
    path('items/<str:code>/', ItemView.as_view()),

    path("purchase/", PurchaseListView.as_view()),
    path("purchase/<str:code>/", PurchaseView.as_view()),
    path("purchase/<str:header_code>/details/", PurchaseDetailListCreateView.as_view()),

    path('sell/', SellListView.as_view()),
    path('sell/<str:code>/', SellView.as_view()),
    path('sell/<str:header_code>/details/', SellDetailListCreateView.as_view()),

    path("report/<str:item_code>/", StockReportView.as_view()),
]
