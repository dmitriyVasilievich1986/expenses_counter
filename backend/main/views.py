from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from datetime import date

from .models import (
    ShopAddress,
    Transaction,
    SubCategory,
    Category,
    Product,
    Price,
    Shop,
)

from .serializers import (
    ShopAddressSerializer,
    TransactionSerializer,
    SubCategorySerializer,
    CategorySerializer,
    ProductSerializer,
    PriceSerializer,
    ShopSerializer,
)


def index_view(request, pk=None, *args, **kwargs):
    return render(request=request, template_name="index.html", context=dict())


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


class PriceViewSet(ModelViewSet):
    serializer_class = PriceSerializer
    queryset = Price.objects.all()


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    def _get_class_object(self, data, ObjectClass, SerializerClass):
        if "id" in data:
            obj = get_object_or_404(ObjectClass, id=data["id"])
        elif "name" in data:
            obj = get_object_or_404(ObjectClass, name=data["name"])
        else:
            obj = ObjectClass.objects.filter(**data).first()
        if obj is not None:
            return obj.id
        obj = SerializerClass(data=data)
        obj.is_valid(raise_exception=True)
        obj.save()
        return obj.data["id"]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["date"] = data.get("date", str(date.today()))
        data["price_full_price"] = data.get(
            "price_full_price", data.get("price_actual_price")
        )
        transaction = TransactionSerializer(
            data={
                "date": data.get("date", str(date.today())),
                "shop": self._get_class_object(data["shop"], Shop, ShopSerializer),
                "price": self._get_class_object(data["price"], Price, PriceSerializer),
                "product": self._get_class_object(
                    data["product"], Product, ProductSerializer
                ),
                "sub_category": self._get_class_object(
                    data["sub_category"], SubCategory, SubCategorySerializer
                ),
            }
        )
        transaction.is_valid(raise_exception=True)
        self.perform_create(transaction)
        headers = self.get_success_headers(transaction.data)
        return Response(
            transaction.instance.json, status=status.HTTP_201_CREATED, headers=headers
        )
