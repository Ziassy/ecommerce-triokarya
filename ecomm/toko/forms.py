from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Contact, Review, UserProfile, Address, ProdukItem, PILIHAN_PEMBAYARAN, PILIHAN_PENGIRIMAN

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nama', 'phone_number', 'jenis_kelamin', 'tanggal_lahir', 'profile_picture']
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['provinsi', 'kabupaten', 'kecamatan', 'kelurahan', 'detail', 'is_primary']

class CheckoutForm(forms.Form):
    alamat_1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Alamat Anda', 'class': 'textinput form-control'}))
    alamat_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartement, Rumah, atau yang lain (opsional)', 'class': 'textinput form-control'}))
    negara = CountryField(blank_label='(Pilih Negara)').formfield(widget=CountrySelectWidget(attrs={'class': 'countryselectwidget form-select'}))
    kode_pos = forms.CharField(widget=forms.TextInput(attrs={'class': 'textinput form-outline', 'placeholder': 'Kode Pos'}))
    simpan_info_alamat = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    opsi_pengiriman = forms.ChoiceField(widget=forms.RadioSelect(), choices=PILIHAN_PENGIRIMAN)
    opsi_pembayaran = forms.ChoiceField(widget=forms.RadioSelect(), choices=PILIHAN_PEMBAYARAN)
    

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        
        
class ProdukItemForm(forms.ModelForm):
    class Meta:
        model = ProdukItem
        fields = ['nama_produk', 'harga', 'harga_diskon', 'slug', 'deskripsi', 'gambar', 'label', 'kategori', 'berat']