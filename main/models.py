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


class Price(models.Model):
    actual_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=False,
        default=0,
    )
    full_price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=0,
        null=True,
    )
    date = models.DateField(auto_now=True, auto_now_add=False, null=False)

    @property
    def price(self):
        return self.actual_price or self.full_price


class Shop(models.Model):
    address = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=150, blank=False, null=False)


class Product(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    sub_category = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="products",
        to="SubCategory",
    )
    price = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="products",
        to="Price",
    )
    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="products",
        to="Shop",
    )
