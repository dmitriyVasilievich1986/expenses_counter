# Generated by Django 4.1.1 on 2023-01-04 21:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_delete_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sub_category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="main.subcategory",
            ),
        ),
    ]
