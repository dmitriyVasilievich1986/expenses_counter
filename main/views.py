from .models import Category, SubCategory, Shop, Price, Product
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from datetime import date

from .serializers import (
    SUBCategorySerializer,
    CategorySerializer,
    ProductSerializer,
    PriceSerializer,
    ShopSerializer,
)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class SubCategoryViewSet(ModelViewSet):
    serializer_class = SUBCategorySerializer
    queryset = SubCategory.objects.all()


class ShopViewSet(ModelViewSet):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()


class PriceViewSet(ModelViewSet):
    serializer_class = PriceSerializer
    queryset = Price.objects.all()


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def _get_class_object(self, data, class_object, serializer_object, name):
        if f"{name}_id" in data:
            obj = get_object_or_404(class_object, pk=data[f"{name}_id"])
            return obj.id
        d = {k.lstrip(f"{name}_"): v for k, v in data.items() if k.startswith(name)}
        obj = class_object.objects.filter(**d).first()
        if obj is not None:
            return obj.id
        obj = serializer_object(data=d)
        obj.is_valid(raise_exception=True)
        obj.save()
        return obj.data["id"]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["price_date"] = data.get("price_date", str(date.today()))
        data["price_full_price"] = data.get(
            "price_full_price", data.get("price_actual_price")
        )
        product = ProductSerializer(
            data={
                "description": data.get("description"),
                "name": data.get("name"),
                "price": self._get_class_object(data, Price, PriceSerializer, "price"),
                "shop": self._get_class_object(data, Shop, ShopSerializer, "shop"),
                "sub_category": self._get_class_object(
                    data, SubCategory, SUBCategorySerializer, "sub_category"
                ),
            }
        )
        product.is_valid(raise_exception=True)
        self.perform_create(product)
        headers = self.get_success_headers(product.data)
        return Response(
            product.instance.json, status=status.HTTP_201_CREATED, headers=headers
        )
