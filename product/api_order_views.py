from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.response import Response

from product.models import Order, Product, DetailedOrder
from product.serializers import OrderSerializer


class OrderList(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = 'id'

    def get_queryset(self):
        return Order.objects.all().order_by('created_at')


def add_product_to_order(order, data):
    quantity = int(data.get('quantity'))
    product_id = data.get('product')

    if quantity <= 0:
        raise ValidationError({'quantity': f'Quantity of product \'{product_id}\' '
                                           f'must be greater than 0'})
    try:
        product = Product.objects.get(pk=product_id)
        if product.stock < quantity:
            raise ValidationError({'quantity': f'Not enough stock of product \'id: {product.id}\' '
                                               f'to complete order'})
        product.stock -= quantity
        # subscribing new stock in cache for avoid conflicts
        cache.set('product_data_{}'.format(product.id), {
            'stock': product.stock,
        })
        Product.objects.filter(pk=product.id).update(stock=product.stock)
    except Product.DoesNotExist:
        raise ValidationError({'product': f'Product with id {product_id} not found'})

    order.price += product.price_excluding_tax * quantity
    order.price_with_tax += product.price_after_taxes() * quantity
    order_item = DetailedOrder.objects.create(order=order, product=product, quantity=quantity)
    order_item.save()


class OrderCreate(CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        with transaction.atomic():
            order = Order.objects.create(price=Decimal(0.00), price_with_tax=Decimal(0.00))
            if isinstance(data, list):
                # I need to secure that the same product is not added twice
                unique_products = {}
                result_data = []
                for item in data:
                    if item.get('product') not in unique_products:
                        unique_products[item.get('product')] = item
                        result_data.append(item)
                    else:
                        # I rather raise an error than to add the sum of the quantities
                        raise ValidationError({'product': f'Product \'{item.get("product")}\' cannot be added twice'})
                for item in result_data:
                    add_product_to_order(order, item)
            else:
                add_product_to_order(order, data)
            order.save()
        return Response(OrderSerializer(order).data, status=201)


class OrderUpdateAndDestroy(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            cache.delete('order_data_{}'.format(order_id))
        return response

    def update(self, request, *args, **kwargs):
        order_id = kwargs.get('id')
        data = request.data
        order = get_object_or_404(Order, id=order_id)
        product = get_object_or_404(Product, id=data.get('product'))
        quantity = int(data.get('quantity'))

        order_item = None
        try:
            order_item = DetailedOrder.objects.get(order=order, product=product)
        except DetailedOrder.DoesNotExist:
            if quantity == 0:
                raise ValidationError({'quantity': 'Cannot possible update quantity to 0 if product is not in order'})
            else:
                order_item = DetailedOrder.objects.create(order=order, product=product, quantity=0)
        try:
            with transaction.atomic():
                if quantity == 0 or order_item.quantity == abs(quantity):
                    order.price -= Decimal(product.price_excluding_tax * order_item.quantity)
                    order.price_with_tax -= Decimal(product.price_after_taxes() * order_item.quantity)
                    product.stock += order_item.quantity
                    product.save()
                    order_item.delete()

                    cache.delete('order_data_{}'.format(order_item.id))
                elif quantity > 0 or quantity < 0:
                    if quantity > product.stock:
                        raise ValidationError(f'Not enough stock of product \'id: {product.id}\' to complete order')
                    if quantity < 0 and order_item.quantity < abs(quantity):
                        raise ValidationError('Cannot remove more products than in order')
                    if quantity > 0:
                        product.stock -= quantity
                    else:
                        product.stock += abs(quantity)
                    product.save()

                    order.price += Decimal(product.price_excluding_tax * quantity)
                    order.price_with_tax += Decimal(product.price_after_taxes() * quantity)
                    order_item.quantity += quantity
                    order_item.save()
                else:
                    add_product_to_order(order, data)

                cache.set('product_data_{}'.format(product.id), {
                    'stock': product.stock,
                })
                cache.set('order_data_{}'.format(order.id), {
                    'price': order.price,
                    'price_with_tax': order.price_with_tax,
                })
                order.save()
        except ValidationError as e:
            return Response(e.detail, status=400)
        return Response(OrderSerializer(order).data, status=200)
