from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, \
    get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from product.models import Product
from product.serializers import ProductSerializer


class ProductsPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = (DjangoFilterBackend,)
    filter_fields = 'id'

    def get_queryset(self):
        if 'in_stock' in self.request.path:
            return Product.objects.filter(stock__gt=0).exclude(stock=1)
        return Product.objects.all()


class ProductCreate(CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        try:
            price_excluding_tax = request.data['price_excluding_tax']
            if price_excluding_tax is not None and float(price_excluding_tax) <= 0.0:
                raise ValidationError({'price_excluding_tax': 'Price excluding tax must be greater than EUR 0.00'})
        except ValueError:
            raise ValidationError({'price_excluding_tax': 'Price excluding tax must be a number'})
        return super().create(request, *args, **kwargs)


class ProductUpdateAndDestroy(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            cache.delete('product_data_{}'.format(product_id))
        return response

    def update(self, request, *args, **kwargs):
        if 'stock' in request.path:
            product_id = kwargs.get('id')
            product = get_object_or_404(Product, pk=product_id)
            stock = request.data.get('stock')
            if stock < 0:
                product.stock -= stock
            else:
                product.stock += stock
            cache.set('product_data_{}'.format(product.id), {
                'stock': product.stock,
            })
            product.save()
            return Response({'message': 'Product stock updated successfully',
                             'product': ProductSerializer(product).data}, status=200)
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            product = response.data
            cache.set('product_data_{}'.format(product['reference']), {
                'name': product['name'],
                'description': product['description'],
                'reference': product['reference'],
                'price_excluding_tax': product['price_excluding_tax'],
                'tax_rate': product['tax_rate'],
            })
        return response
