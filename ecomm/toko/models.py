from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime


PILIHAN_KATEGORI = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
    ('C', 'Cosmetic')
)

PILIHAN_LABEL = (
    ('NEW', 'primary'),
    ('SALE', 'info'),
    ('BEST', 'danger'),
)

PILIHAN_PEMBAYARAN = (
    ('P', 'Paypal'),
    ('C', 'COD'),
    ('T', 'Transfer Manual (BCA)'),
)

JENIS_KELAMIN_CHOICES = [
    ("L", 'Laki-laki'),
    ("P", 'Perempuan'),
]

PILIHAN_PENGIRIMAN = (
    ('PR', 'Kurir Pribadi'),
    ('EX', 'Kurir Eksternal'),
)

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES)
    tanggal_lahir = models.DateField(default=datetime.date(1990, 1, 1))
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.nama
    
class Provinsi(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Kabupaten(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    id_provinsi = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Kecamatan(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    id_kabupaten = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Kelurahan(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    id_kecamatan = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE)
    kabupaten = models.ForeignKey(Kabupaten, on_delete=models.CASCADE)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE)
    kelurahan = models.ForeignKey(Kelurahan, on_delete=models.CASCADE)
    kode_pos = models.CharField(max_length=20, default='')
    detail = models.CharField(max_length=255, default='')
    nama_penerima = models.CharField(max_length=255, default='')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Address"

class ProdukItem(models.Model):
    nama_produk = models.CharField(max_length=100)
    harga = models.FloatField()
    harga_diskon = models.FloatField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    deskripsi = models.TextField()
    gambar = models.ImageField(upload_to='product_pics')
    label = models.CharField(choices=PILIHAN_LABEL, max_length=4)
    kategori = models.CharField(choices=PILIHAN_KATEGORI, max_length=2)
    berat = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.nama_produk} - ${self.harga}"

    def get_absolute_url(self):
        return reverse("toko:produk-detail", kwargs={
            "slug": self.slug
            })

    def get_add_to_cart_url(self):
        return reverse("toko:add-to-cart", kwargs={
            "slug": self.slug
            })
    
    def get_remove_from_cart_url(self):
        return reverse("toko:remove-from-cart", kwargs={
            "slug": self.slug
            })
        
class Review(models.Model):
    produk = models.ForeignKey(ProdukItem, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
    
class OrderProdukItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    produk_item = models.ForeignKey(ProdukItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.produk_item.nama_produk}"

    def get_total_harga_item(self):
        return self.quantity * self.produk_item.harga
    
    def get_total_harga_diskon_item(self):
        return self.quantity * self.produk_item.harga_diskon

    def get_total_hemat_item(self):
        return self.get_total_harga_item() - self.get_total_harga_diskon_item()
    
    def get_total_item_keseluruan(self):
        if self.produk_item.harga_diskon:
            return self.get_total_harga_diskon_item()
        return self.get_total_harga_item()
    
    def get_total_hemat_keseluruhan(self):
        if self.produk_item.harga_diskon:
            return self.get_total_hemat_item()
        return 0


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    produk_items = models.ManyToManyField(OrderProdukItem)
    tanggal_mulai = models.DateTimeField(auto_now_add=True)
    tanggal_order = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    alamat_pengiriman = models.ForeignKey('AlamatPengiriman', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    delivery_method = models.CharField(max_length=2,choices=PILIHAN_PENGIRIMAN,default='PR')

    def __str__(self):
        return self.user.username

     
    def get_total_harga_order(self):
        total = 0
        for order_produk_item in self.produk_items.all():
            total += order_produk_item.get_total_item_keseluruan()
        return total
    
    def get_total_diskon_order(self):
        total_diskon = 0
        for order_produk_item in self.produk_items.all():
            total_diskon += order_produk_item.get_total_hemat_keseluruhan()
        return total_diskon

class AlamatPengiriman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detail_alamat = models.CharField(max_length=255, default='')
    provinsi = models.CharField(max_length=100, default='')
    kabupaten = models.CharField(max_length=100, default='')
    kecamatan = models.CharField(max_length=100, default='')
    kelurahan = models.CharField(max_length=100, default='')
    kode_pos = models.CharField(max_length=10, default='')
    nama_penerima = models.CharField(max_length=255, default='')

    def __str__(self):
        return f"{self.user.username} - {self.detail_alamat}"

    class Meta:
        verbose_name_plural = 'AlamatPengiriman'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_option = models.CharField(choices=PILIHAN_PEMBAYARAN, max_length=1)
    charge_id = models.CharField(max_length=50)

    def __self__(self):
        return self.user.username
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_option} - {self.amount}"
    
    class Meta:
        verbose_name_plural = 'Payment'
        
        
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.name