from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render

from .models import (
    ShopAddress,
    Transaction,
    SubCategory,
    Category,
    Product,
    Shop,
)

from .serializers import (
    ShopAddressSerializer,
    TransactionSerializer,
    SubCategorySerializer,
    CategorySerializer,
    ProductSerializer,
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


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
