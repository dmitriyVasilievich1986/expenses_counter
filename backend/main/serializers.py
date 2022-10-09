from .models import Category, SubCategory, Shop, Price, Product
from rest_framework.serializers import ModelSerializer


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SUBCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class PriceSerializer(ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
