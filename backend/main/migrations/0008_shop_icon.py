# Generated by Django 4.1.1 on 2024-02-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0007_shopaddress_local_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="icon",
            field=models.CharField(default="", max_length=150),
            preserve_default=False,
        ),
    ]
