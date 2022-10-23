from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)


class SubCategory(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        related_name="sub_categories",
        on_delete=models.CASCADE,
        to="Category",
    )


class Shop(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)


class ShopAddress(models.Model):
    address = models.CharField(max_length=150, blank=False, null=False)

    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="addresses",
        to="Shop",
    )


class Transaction(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False, null=False)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=False,
        default=0,
    )

    product = models.ForeignKey(
        related_name="transanctions",
        on_delete=models.CASCADE,
        to="Product",
    )
    sub_category = models.ForeignKey(
        related_name="transanctions",
        on_delete=models.CASCADE,
        to="SubCategory",
    )
    shop = models.ForeignKey(
        related_name="transanctions",
        on_delete=models.CASCADE,
        to="Shop",
    )


class Product(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
