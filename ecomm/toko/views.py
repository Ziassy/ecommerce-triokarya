from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views import generic
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from .forms import CheckoutForm, ContactForm
from .models import ProdukItem, OrderProdukItem, Order, AlamatPengiriman, Payment, Contact, PILIHAN_KATEGORI

class ProductList(generic.ListView):
    template_name = 'carousel.html'
    queryset = ProdukItem.objects.all()
    # paginate_by = 4
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = {
            'S': 'Shirt',
            'SW': 'Sportswear',
            'OW': 'Outerwear',
            'C': 'Cosmetic'
        }  # Dictionary mapping category codes to their corresponding names
        selected_categories_values = self.request.GET.getlist('category')  # Get selected categories from the request
        selected_categories_keys = [category for category, name in categories.items() if name in selected_categories_values]
        sorted_products = self.queryset

        if selected_categories_keys:
            sorted_products = sorted_products.filter(kategori__in=selected_categories_keys)

        context['categories'] = categories.values()
        context['selected_categories'] = selected_categories_values
        context['object_list'] = sorted_products

        return context


class HomeListView(generic.ListView):
    template_name = 'home.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4

# Handle insecure Direct object reference, need login
@method_decorator(permission_required('app.view_produk'), name='dispatch') 
class ProductDetailView(generic.DetailView):
    template_name = 'product_detail.html'
    queryset = ProdukItem.objects.all()
    
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    
class ContactPageView(generic.FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('toko:contact_success')

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())
    
def contact_success(request):
    return render(request, 'success-contact.html')


def about_view(request):
    return render(request, 'about.html')

def empty_view_order_summary(request):
    return render(request, 'empty_order_summary.html')
    
    
class CheckoutView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        order = get_object_or_404(Order, user=self.request.user, ordered=False)

        # Handle Insecure direct object reference
        # Check if the order belongs to the current user
        if order.user != self.request.user:
            raise PermissionDenied('You are not authorized to access this order.')
        
        
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.produk_items.count() == 0:
                messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        context = {
            'form': form,
            'keranjang': order,
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                alamat_1 = form.cleaned_data.get('alamat_1')
                alamat_2 = form.cleaned_data.get('alamat_2')
                negara = form.cleaned_data.get('negara')
                kode_pos = form.cleaned_data.get('kode_pos')
                opsi_pembayaran = form.cleaned_data.get('opsi_pembayaran')
                
                 # Validate opsi_pembayaran to prevent unauthorized payment method selection
                allowed_payment_methods = ['P', 'S']  # Add the allowed payment method codes
                
                # Parameter Tampering Prevention
                if opsi_pembayaran not in allowed_payment_methods:
                    raise PermissionDenied('Invalid payment method selected')
                
                alamat_pengiriman = AlamatPengiriman(
                    user=self.request.user,
                    alamat_1=alamat_1,
                    alamat_2=alamat_2,
                    negara=negara,
                    kode_pos=kode_pos,
                )

                alamat_pengiriman.save()
                order.alamat_pengiriman = alamat_pengiriman
                order.save()
                if opsi_pembayaran == 'P':
                    return redirect('toko:payment', payment_method='paypal')
                else:
                    return redirect('toko:payment', payment_method='stripe')

            messages.warning(self.request, 'Gagal checkout')
            return redirect('toko:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('toko:order-summary')

class PaymentView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        template_name = 'payment.html'
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            paypal_data = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': order.get_total_harga_order,
                'item_name': f'Pembayaran belajanan order: {order.id}',
                'invoice': f'{order.id}-{timezone.now().timestamp()}' ,
                'currency_code': 'USD',
                'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': self.request.build_absolute_uri(reverse('toko:paypal-return')),
                'cancel_return': self.request.build_absolute_uri(reverse('toko:paypal-cancel')),
            }
        
            qPath = self.request.get_full_path()
            isPaypal = 'paypal' in qPath
        
            form = PayPalPaymentsForm(initial=paypal_data)
            context = {
                'paypalform': form,
                'order': order,
                'is_paypal': isPaypal,
            }
            return render(self.request, template_name, context)

        except ObjectDoesNotExist:
            return redirect('toko:checkout')

class OrderSummaryView(LoginRequiredMixin, generic.TemplateView):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'keranjang': order
            }
            template_name = 'order_summary.html'
            return render(self.request, template_name, context)
        except ObjectDoesNotExist:
            # messages.error(self.request, 'Tidak ada pesanan yang aktif')
             return redirect('toko:empty-order-summary')

def add_to_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_produk_item, _ = OrderProdukItem.objects.get_or_create(
            produk_item=produk_item,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                order_produk_item.quantity += 1
                order_produk_item.save()
                pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                messages.info(request, pesan)
                return redirect('toko:produk-detail', slug = slug)
            else:
                order.produk_items.add(order_produk_item)
                messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
                return redirect('toko:produk-detail', slug = slug)
        else:
            tanggal_order = timezone.now()
            order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
            order.produk_items.add(order_produk_item)
            messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
            return redirect('toko:produk-detail', slug = slug)
    else:
        return redirect('/accounts/login')

def remove_from_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_query = Order.objects.filter(
            user=request.user, ordered=False
        )
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                try: 
                    order_produk_item = OrderProdukItem.objects.filter(
                        produk_item=produk_item,
                        user=request.user,
                        ordered=False
                    )[0]
                    
                    order.produk_items.remove(order_produk_item)
                    order_produk_item.delete()

                    pesan = f"ProdukItem sudah dihapus"
                    messages.info(request, pesan)
                    return redirect('toko:produk-detail',slug = slug)
                except ObjectDoesNotExist:
                    print('Error: order ProdukItem sudah tidak ada')
            else:
                messages.info(request, 'ProdukItem tidak ada')
                return redirect('toko:produk-detail',slug = slug)
        else:
            messages.info(request, 'ProdukItem tidak ada order yang aktif')
            return redirect('toko:produk-detail',slug = slug)
    else:
        return redirect('/accounts/login')

@csrf_exempt
def paypal_return(request):
    if request.user.is_authenticated:
        try:
            print('paypal return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'P' # paypal kalai 'S' stripe
            payment.charge_id = f'{order.id}-{timezone.now()}'
            payment.timestamp = timezone.now()
            payment.save()

            order_produk_item = OrderProdukItem.objects.filter(user=request.user,ordered=False)
            order_produk_item.update(ordered=True)
            
            order.payment = payment
            order.ordered = True
            order.save()

            messages.info(request, 'Pembayaran sudah diterima, terima kasih')
            return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            messages.error(request, 'Periksa kembali pesananmu')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')

@csrf_exempt
def paypal_cancel(request):
    messages.error(request, 'Pembayaran dibatalkan')
    return redirect('toko:order-summary')