# Generated by Django 4.1.1 on 2023-01-04 21:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0005_product_sub_category"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="sub_category",
        ),
    ]
