# Generated by Django 4.1.1 on 2022-10-23 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_transaction_price"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Price",
        ),
    ]
