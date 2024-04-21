"""
URL configuration for store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path

import product.api_product_views
import product.api_order_views

urlpatterns = [
                  path('admin/', admin.site.urls),

                  path('api/v1/products/', product.api_product_views.ProductList.as_view()),
                  path('api/v1/products/in_stock/', product.api_product_views.ProductList.as_view()),
                  path('api/v1/products/new/', product.api_product_views.ProductCreate.as_view()),
                  path('api/v1/products/<int:id>/', product.api_product_views.ProductUpdateAndDestroy.as_view()),
                  path('api/v1/products/stock/<int:id>/', product.api_product_views.ProductUpdateAndDestroy.as_view()),

                  path('api/v1/orders/', product.api_order_views.OrderList.as_view()),
                  path('api/v1/orders/new/', product.api_order_views.OrderCreate.as_view()),
                  path('api/v1/orders/<int:id>/', product.api_order_views.OrderUpdateAndDestroy.as_view()),
                  path('api/v1/orders/<int:id>/', product.api_order_views.OrderUpdateAndDestroy.as_view()),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
