# Generated by Django 5.1.7 on 2025-03-13 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('Electronics', 'Electronics'), ('Clothing', 'Clothing'), ('Home', 'Home & Garden'), ('Books', 'Books'), ('Sports', 'Sports'), ('Collectibles', 'Collectibles'), ('Toys', 'Toys'), ('Beauty', 'Beauty & Personal Care'), ('Automotive', 'Automotive'), ('Other', 'Other')], default='Other', max_length=100),
        ),
    ]
