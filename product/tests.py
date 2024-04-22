from rest_framework.test import APITestCase

from product.models import Product, Order


# Create your tests here.
class ProductCreateTestCase(APITestCase):
    def test_create_product(self):
        url = '/api/v1/products/new/'
        data = {
            'name': 'Product 1',
            'description': 'Description of product 1',
            'reference': 'REF-001',
            'stock': 10,
            'currency': 'EUR',
            'tax_rate': 21.00,
            'price_excluding_tax': 100.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Product 1')
        self.assertTrue(Product.objects.get().created_at is not None)

    def test_create_product_with_invalid_data(self):
        url = '/api/v1/products/new/'
        data = {
            'name': 'Product 1',
            'description': 'Description of product 1',
            'reference': 'REF-001',
            'stock': 10,
            'currency': 'EUR',
            'tax_rate': 21.00,
            'price_excluding_tax': -100.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Product.objects.count(), 0)

    def test_destroy_product(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = f'/api/v1/products/{product.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.count(), 0)

    def test_update_product(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = f'/api/v1/products/{product.id}/'
        data = {
            'name': 'Product 2',
            'description': 'Description of product 2',
            'reference': 'REF-002',
            'stock': 20,
            'currency': 'USD',
            'tax_rate': 10.00,
            'price_excluding_tax': 200.00
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Product 2')
        self.assertEqual(Product.objects.get().description, 'Description of product 2')
        self.assertEqual(Product.objects.get().reference, 'REF-002')
        self.assertEqual(Product.objects.get().stock, 20)
        self.assertEqual(Product.objects.get().currency, 'USD')
        self.assertEqual(Product.objects.get().tax_rate, 10.00)
        self.assertEqual(Product.objects.get().price_excluding_tax, 200.00)
        self.assertTrue(Product.objects.get().created_at is not None)

    def test_update_stock(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = f'/api/v1/products/stock/{product.id}/'
        data = {
            'stock': 5
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().stock, 15)
        self.assertTrue(Product.objects.get().created_at is not None)

    def test_get_products_with_stock(self):
        Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                               stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        Product.objects.create(name='Product 2', description='Description of product 2', reference='REF-002',
                               stock=0, currency='USD', tax_rate=10.00, price_excluding_tax=200.00)
        url = f'/api/v1/products/in_stock/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_all_products(self):
        Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                               stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        Product.objects.create(name='Product 2', description='Description of product 2', reference='REF-002',
                               stock=0, currency='USD', tax_rate=10.00, price_excluding_tax=200.00)
        url = f'/api/v1/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_get_product_by_id(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = f'/api/v1/products/{product.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Product 1')
        self.assertEqual(response.data['description'], 'Description of product 1')
        self.assertEqual(response.data['reference'], 'REF-001')
        self.assertEqual(response.data['stock'], 10)
        self.assertEqual(response.data['currency'], 'EUR')
        self.assertEqual(response.data['tax_rate'], 21.00)
        self.assertEqual(response.data['price_excluding_tax'], 100.00)
        self.assertTrue(response.data['created_at'] is not None)


class OrderCreateTestCase(APITestCase):

    def test_create_order(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = '/api/v1/orders/new/'
        data = {
            'product': product.id,
            'quantity': 5
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['product_list']), 1)
        self.assertEqual(Order.objects.count(), 1)
        self.assertTrue(Order.objects.get().created_at is not None)
        self.assertTrue(Order.objects.get().updated_at is not None)

        product: Product = Product.objects.filter(pk=product.id).first()
        self.assertEqual(product.stock, 5)

    def test_create_order_with_three_products(self):
        product_2 = Product.objects.create(name='Product 2', description='Description of product 2',
                                           reference='REF-002',
                                           stock=20, currency='EUR', tax_rate=21.00, price_excluding_tax=90.00)
        product_3 = Product.objects.create(name='Product 3', description='Description of product 3',
                                           reference='REF-003',
                                           stock=50, currency='EUR', tax_rate=10.00, price_excluding_tax=110.00)
        product_4 = Product.objects.create(name='Product 4', description='Description of product 4',
                                           reference='REF-004',
                                           stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)

        url = '/api/v1/orders/new/'
        data = [
            {
                'product': product_2.id,
                'quantity': 10
            },
            {
                'product': product_3.id,
                'quantity': 20
            },
            {
                'product': product_4.id,
                'quantity': 5
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['product_list']), 3)
        self.assertEqual(Order.objects.count(), 1)
        self.assertTrue(Order.objects.get().created_at is not None)
        self.assertTrue(Order.objects.get().updated_at is not None)

        product: Product = Product.objects.filter(pk=product_2.id).first()
        self.assertEqual(product.stock, 10)

        product: Product = Product.objects.filter(pk=product_3.id).first()
        self.assertEqual(product.stock, 30)

        product: Product = Product.objects.filter(pk=product_4.id).first()
        self.assertEqual(product.stock, 5)

    def test_create_order_with_same_product_twice(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        url = '/api/v1/orders/new/'
        data = [
            {
                'product': product.id,
                'quantity': 5
            },
            {
                'product': product.id,
                'quantity': 10
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_create_order_with_invalid_data(self):
        url = '/api/v1/orders/new/'
        data = {
            'product': 1,
            'quantity': 0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_destroy_order(self):
        order = Order.objects.create(price=0.00, price_with_tax=0.00)
        url = f'/api/v1/orders/{order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Order.objects.count(), 0)

    def test_update_order(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        order = Order.objects.create(price=0.00, price_with_tax=0.00)
        url = f'/api/v1/orders/{order.id}/'
        data = {
            'product': product.id,
            'quantity': 5
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(len(response.data['product_list']), 1)
        self.assertEqual(Order.objects.get().price, 500.00)
        self.assertEqual(Order.objects.get().price_with_tax, 605.00)
        self.assertTrue(Order.objects.get().created_at is not None)
        self.assertTrue(Order.objects.get().updated_at is not None)

        product: Product = Product.objects.filter(pk=product.id).first()
        self.assertEqual(product.stock, 5)

    def test_get_orders(self):
        product = Product.objects.create(name='Product 1', description='Description of product 1', reference='REF-001',
                                         stock=10, currency='EUR', tax_rate=21.00, price_excluding_tax=100.00)
        order = Order.objects.create(price=0.00, price_with_tax=0.00)
        url = '/api/v1/orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)