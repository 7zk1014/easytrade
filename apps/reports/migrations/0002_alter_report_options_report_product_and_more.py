# Generated by Django 5.1.7 on 2025-03-18 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_payment_status_alter_order_status"),
        ("products", "0005_product_status"),
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="report",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddField(
            model_name="report",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.product",
            ),
        ),
        migrations.AddField(
            model_name="report",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="report",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="orders.order",
            ),
        ),
        migrations.AlterField(
            model_name="report",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("in_progress", "In Progress"),
                    ("resolved", "Resolved"),
                    ("closed", "Closed"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
