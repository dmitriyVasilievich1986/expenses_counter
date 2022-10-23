from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    @property
    def json(self):
        payload = {
            "id": self.id,
            "name": self.name,
        }
        return payload


class SubCategory(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        related_name="sub_categories",
        on_delete=models.CASCADE,
        to="Category",
    )

    @property
    def json(self):
        payload = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.json,
        }
        return payload


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

    @property
    def price(self):
        return self.actual_price or self.full_price

    @property
    def json(self):
        payload = {
            "id": self.id,
            "price": str(self.price),
        }
        return payload


class Shop(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    @property
    def json(self):
        payload = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "addresses": [x.address for x in self.addresses.all()],
        }
        return payload


class ShopAddress(models.Model):
    address = models.CharField(max_length=150, blank=False, null=False)

    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="addresses",
        to="Shop",
    )


class Transaction(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=False, null=False)

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
    price = models.ForeignKey(
        related_name="transanctions",
        on_delete=models.CASCADE,
        to="Price",
    )
    shop = models.ForeignKey(
        related_name="transanctions",
        on_delete=models.CASCADE,
        to="Shop",
    )

    @property
    def json(self):
        payload = {
            "id": self.id,
            "date": self.date,
            "shop": self.shop.json,
            "price": self.price.json,
            "product": self.product.json,
            "sub_category": self.sub_category.json,
        }
        return payload


class Product(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    @property
    def json(self):
        payload = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        return payload
