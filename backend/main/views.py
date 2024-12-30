from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from dateutil.relativedelta import relativedelta  # type: ignore
from django.db.models import Count, F, Sum
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status
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

    def create(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        category = Category.objects.get(pk=request.data["sub_category"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer._validated_data["sub_category"] = category
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        queryset = self.filter_queryset(self.get_queryset()).order_by("-sub_category")

        if (page := self.paginate_queryset(queryset)) is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if "sub_category" in request.data:
            serializer._validated_data["sub_category"] = Category.objects.get(
                pk=request.data["sub_category"]
            )
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def create(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        address = ShopAddress.objects.get(pk=request.data["address"])
        product = Product.objects.get(pk=request.data["product"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer._validated_data["address"] = address
        serializer._validated_data["product"] = product
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def retrieve(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        instance = self.get_object()
        serializer = TransactionDetailedSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def date_range(self, request: HttpRequest) -> HttpResponse:
        start = request.data["start_date"]
        end = request.data["end_date"]
        transactions = Transaction.objects.filter(date__gte=start, date__lte=end)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def month_spendings(self, request: HttpRequest) -> HttpResponse:
        current_date = datetime.strptime(request.data["date"], "%Y-%m-%d").date()
        start = current_date.replace(day=1)
        end = start + relativedelta(months=1)
        transactions = (
            Transaction.objects.filter(date__gte=start, date__lt=end)
            .annotate(summary=F("price") * F("count"))
            .values("date")
            .annotate(summary=Sum("summary"))
            .order_by("date")
        )
        return Response(transactions)

    def update(
        self, request: HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> HttpResponse:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if "address" in request.data:
            serializer._validated_data["address"] = ShopAddress.objects.get(
                pk=request.data["address"]
            )
        if "product" in request.data:
            serializer._validated_data["product"] = Product.objects.get(
                pk=request.data["product"]
            )
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
