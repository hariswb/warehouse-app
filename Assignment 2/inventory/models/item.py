from django.db import models
from .base import Base

class Item(Base):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name