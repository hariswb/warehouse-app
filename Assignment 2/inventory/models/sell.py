from django.db import models
from .base import Base
from .item import Item


class Sell(Base):
    code = models.CharField(max_length=20, unique=True)
    date = models.DateField()
    description = models.TextField(blank=True)

class SellDetail(Base):
    header = models.ForeignKey(Sell, on_delete=models.CASCADE, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
