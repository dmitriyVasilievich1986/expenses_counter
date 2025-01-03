# Generated by Django 4.1.1 on 2022-10-23 09:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="price",
            name="date",
        ),
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
        migrations.RemoveField(
            model_name="product",
            name="shop",
        ),
        migrations.RemoveField(
            model_name="product",
            name="sub_category",
        ),
        migrations.RemoveField(
            model_name="shop",
            name="address",
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                (
                    "price",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transanctions",
                        to="main.price",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transanctions",
                        to="main.product",
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transanctions",
                        to="main.shop",
                    ),
                ),
                (
                    "sub_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transanctions",
                        to="main.subcategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShopAddress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.CharField(max_length=150)),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to="main.shop",
                    ),
                ),
            ],
        ),
    ]
