from __future__ import annotations

from typing import Any, TypedDict

from django.db.models import Count
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Category, Product, Shop, ShopAddress, SubCategory, Transaction
from .serializers import (
    CategoryDetailedSerializer,
    CategorySerializer,
    ProductDetailedSerializer,
    ShopAddressSerializer,
    ShopDetailedSerializer,
    ShopSerializer,
    SubCategorySerializer,
    TransactionDetailedSerializer,
    TransactionSerializer,
)


class ProductPrice(TypedDict):
    product_id: int


def index_view(request: HttpRequest, resource: str | int | None = None) -> HttpResponse:
    return render(request=request, template_name="index.html", context=dict())


def images_view(request: HttpRequest, pk: int | None = None) -> HttpResponse:
    return HttpResponse(status=404)


class ProductViewSet(ModelViewSet):
    serializer_class = ProductDetailedSerializer
    queryset = Product.objects.all()

    @action(detail=False, methods=["post"])
    def price(self, request: HttpRequest) -> HttpResponse:
        data: ProductPrice = request.data
        transaction = (
            Transaction.objects.filter(product_id=data["product_id"])
            .order_by("-date")
            .first()
        )
        serializer = TransactionDetailedSerializer(transaction)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def popular(self, request: HttpRequest) -> HttpResponse:
        address = ShopAddress.objects.get(pk=request.data["address"])
        popular_products = (
            Transaction.objects.filter(address=address)
            .values("product")
            .annotate(total=Count("product"))
            .order_by("-total")[:5]
        )
        transactions = [
            Transaction.objects.filter(product_id=x["product"]).first()
            for x in popular_products
        ]
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class ShopAddressViewSet(ModelViewSet):
    serializer_class = ShopAddressSerializer
    queryset = ShopAddress.objects.all()


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def retrieve(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        instance = self.get_object()
        serializer = CategoryDetailedSerializer(instance)
        return Response(serializer.data)


class SubCategoryViewSet(ModelViewSet):
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()


class ShopViewSet(ModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()

    def retrieve(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        instance = self.get_object()
        serializer = ShopDetailedSerializer(instance)
        return Response(serializer.data)


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionDetailedSerializer
    queryset = Transaction.objects.all()
