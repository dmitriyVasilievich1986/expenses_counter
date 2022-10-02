from .models import Category, SubCategory, Shop, Price, Product
from rest_framework.viewsets import ModelViewSet

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
