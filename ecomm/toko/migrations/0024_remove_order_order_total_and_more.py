# Generated by Django 4.2 on 2024-07-31 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0023_order_order_total_order_shipping_cost_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_total',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_option',
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_courier',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_cost',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
