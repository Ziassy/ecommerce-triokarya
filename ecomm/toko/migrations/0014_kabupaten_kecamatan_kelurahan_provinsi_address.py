# Generated by Django 4.2 on 2024-05-20 12:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('toko', '0013_rename_nomor_hp_userprofile_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kabupaten',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('id_provinsi', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Kecamatan',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('id_kabupaten', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Kelurahan',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('id_kecamatan', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Provinsi',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.CharField(max_length=255)),
                ('is_primary', models.BooleanField(default=False)),
                ('kabupaten', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toko.kabupaten')),
                ('kecamatan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toko.kecamatan')),
                ('kelurahan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toko.kelurahan')),
                ('provinsi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='toko.provinsi')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
