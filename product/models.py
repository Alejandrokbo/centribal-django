from decimal import Decimal

from django.db import models


# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField()
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, default='EUR')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    price_excluding_tax = models.DecimalField(max_digits=10, decimal_places=2)

    def price_after_taxes(self) -> Decimal:
        return round(self.price_excluding_tax + self.price_excluding_tax * self.tax_rate / 100, 2)

    def __str__(self):
        return f'{self.reference} - {self.name}'

    class Meta:
        db_table = 'product'
        ordering = ['created_at']


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_with_tax = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    product_list = models.ManyToManyField(Product, through='DetailedOrder')

    def __str__(self):
        return f'Order {self.id}'

    class Meta:
        db_table = 'order'
        ordering = ['created_at']


class DetailedOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.order} - {self.product}'

    class Meta:
        db_table = 'detailed_order'
        ordering = ['order']
