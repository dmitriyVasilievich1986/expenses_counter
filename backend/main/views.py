from __future__ import annotations

from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Shop, ShopAddress, SubCategory, Transaction
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ShopAddressSerializer,
    ShopSerializer,
    SubCategorySerializer,
    TransactionSerializer,
)


def index_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    return render(request=request, template_name="index.html", context=dict())


def images_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    return HttpResponse(status=404)


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ShopAddressViewSet(ModelViewSet):
    serializer_class = ShopAddressSerializer
    queryset = ShopAddress.objects.all()


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class SubCategoryViewSet(ModelViewSet):
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()


class ShopViewSet(ModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
