# Generated by Django 4.2 on 2024-08-04 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0029_alamatpengiriman_nomor_handphone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_option',
            field=models.CharField(choices=[('C', 'COD'), ('T', 'Transfer Manual (BCA)')], max_length=1),
        ),
    ]
