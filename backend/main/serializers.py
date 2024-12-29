from rest_framework.serializers import ModelSerializer

from .models import Category, Product, Shop, ShopAddress, SubCategory, Transaction


class ShopAddressSerializer(ModelSerializer):
    class Meta:
        model = ShopAddress
        fields = "__all__"


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CategoryDetailedSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        depth = 1


class SubCategorySerializer(ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class ShopDetailedSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"
        depth = 1


class ProductDetailedSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        depth = 1


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        depth = 1


class TransactionDetailedSerializer(ModelSerializer):
    product = ProductDetailedSerializer()
    address = ShopAddressSerializer()

    class Meta:
        model = Transaction
        fields = "__all__"
