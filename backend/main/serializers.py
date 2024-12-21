from rest_framework.serializers import ModelSerializer

from .models import Category, Product, Shop, ShopAddress, SubCategory, Transaction


class ShopAddressSerializer(ModelSerializer):
    class Meta:
        model = ShopAddress
        fields = "__all__"


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
