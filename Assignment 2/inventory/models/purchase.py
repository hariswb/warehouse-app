from django.db import models
from .base import Base
from .item import Item

class Purchase(Base):
    code = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    description = models.TextField(blank=True)

class PurchaseDetail(Base):
    header = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

