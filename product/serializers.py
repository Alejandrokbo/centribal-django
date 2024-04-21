from rest_framework import serializers

from product.models import Product, DetailedOrder, Order


def get_day_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix


class DetailedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailedOrder
        fields = 'quantity'
        read_only_fields = 'id'


class ProductSerializer(serializers.ModelSerializer):
    description = serializers.CharField(min_length=2, max_length=255)
    name = serializers.CharField(min_length=2, max_length=255)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    price_excluding_tax = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    price_after_taxes = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False,
                                                 allow_null=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'reference', 'description', 'currency', 'stock', 'tax_rate', 'price_excluding_tax',
                  'price_after_taxes', 'created_at')
        read_only_fields = ('id', 'created_at')

    def to_representation(self, instance):
        product = super().to_representation(instance)
        product['price_after_taxes'] = round(float(instance.price_excluding_tax) + float(
            instance.price_excluding_tax) * float(instance.tax_rate) / 100, 2)
        day_suffix = get_day_suffix(instance.created_at.day)
        product['created_at'] = instance.created_at.strftime(f'%B {instance.created_at.day}{day_suffix} %Y - %H:%M')
        return product


class OrderSerializer(serializers.ModelSerializer):
    product_list = ProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'price', 'price_with_tax', 'created_at', 'updated_at', 'product_list')

    def to_representation(self, instance):
        order = super().to_representation(instance)
        order['price'] = float(instance.price)
        order['price_with_tax'] = float(instance.price_with_tax)
        order['product_list'] = ProductSerializer(instance.product_list, many=True).data
        day_suffix = get_day_suffix(instance.created_at.day)
        order['created_at'] = instance.created_at.strftime(f'%B {instance.created_at.day}{day_suffix} %Y - %H:%M')
        day_suffix = get_day_suffix(instance.updated_at.day)
        order['updated_at'] = instance.updated_at.strftime(f'%B {instance.updated_at.day}{day_suffix} %Y - %H:%M')
        return order
