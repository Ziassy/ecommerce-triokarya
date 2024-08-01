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
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from .utils import get_shipping_cost  # Import fungsi API



from .forms import CheckoutForm, ContactForm, ReviewForm, UserProfileForm, AddressForm
from .models import ProdukItem, OrderProdukItem, Order, AlamatPengiriman, Payment, UserProfile, Address, Provinsi, Kabupaten, Kecamatan, Kelurahan

class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'
    form_class = UserProfileForm

    def get(self, request, *args, **kwargs):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user)
        form = self.form_class(instance=profile)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user)
        form = self.form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('toko:profile')
        return render(request, self.template_name, {'form': form})
    
class AddressView(LoginRequiredMixin, View):
    template_name = 'address_form.html'

    def get(self, request, pk=None):
        if pk:
            address = get_object_or_404(Address, pk=pk, user=request.user)
            form = AddressForm(instance=address)
        else:
            form = AddressForm()

        provinsi_list = Provinsi.objects.all()
        kabupaten_list = Kabupaten.objects.all()
        kecamatan_list = Kecamatan.objects.all()
        kelurahan_list = Kelurahan.objects.all()
        
        return render(request, self.template_name, {
            'form': form,
            'provinsi_list': provinsi_list,
            'kabupaten_list': kabupaten_list,
            'kecamatan_list': kecamatan_list,
            'kelurahan_list': kelurahan_list
        })

    def post(self, request, pk=None):
        if pk:
            address = get_object_or_404(Address, pk=pk, user=request.user)
            form = AddressForm(request.POST, instance=address)
        else:
            form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_primary:
                Address.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

            address.save()
            return redirect('toko:address_list')

        provinsi_list = Provinsi.objects.all()
        kabupaten_list = Kabupaten.objects.all()
        kecamatan_list = Kecamatan.objects.all()
        kelurahan_list = Kelurahan.objects.all()

        return render(request, self.template_name, {
            'form': form,
            'provinsi_list': provinsi_list,
            'kabupaten_list': kabupaten_list,
            'kecamatan_list': kecamatan_list,
            'kelurahan_list': kelurahan_list
        })

class AddressListView(LoginRequiredMixin, View):
    template_name = 'address_list.html'

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        return render(request, self.template_name, {'addresses': addresses})
    
class AddressDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.delete()
        return redirect('toko:address_list')

class ProductList(generic.ListView):
    template_name = 'carousel.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 6  # Menentukan jumlah item per halaman

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(nama_produk__icontains=keyword)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = {
            'EP': 'Epson',
            'CN': 'Cannon',
            'BR': 'Brother',
            'HP': 'HP'
        }
        selected_categories_values = self.request.GET.getlist('category')
        selected_categories_keys = [category for category, name in categories.items() if name in selected_categories_values]
        sorted_products = self.get_queryset()  # Use filtered queryset to get keyword search & filter

        if selected_categories_keys:
            sorted_products = sorted_products.filter(kategori__in=selected_categories_keys)
            
        # Calculate average rating for each product
        for produk in sorted_products:
            reviews = produk.reviews.all()
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            average_rating = round(average_rating, 1) if average_rating else 0
            produk.average_rating = average_rating
            produk.total_reviews = reviews.count()
        
        paginator = Paginator(sorted_products, self.paginate_by)
        page = self.request.GET.get('page')
        products = paginator.get_page(page)

        context['categories'] = categories.values()
        context['selected_categories'] = selected_categories_values
        context['object_list'] = products  # Pass paginated products to the context

        if 'carousel' in self.request.path:
            context['show_search_icon'] = True
            context['keyword'] = self.request.GET.get('keyword', '')  # Pass keyword to the context
        else:
            context['show_search_icon'] = False

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produk = self.get_object()
        reviews = produk.reviews.all()
        
        # Calculate average rating and round it to one decimal place
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        average_rating = round(average_rating, 1) if average_rating else 0
        
        total_reviews = reviews.count()
        
        context['reviews'] = reviews
        context['average_rating'] = average_rating
        context['total_reviews'] = total_reviews
        context['has_purchased'] = has_purchased_product(self.request.user, produk)
        return context

def has_purchased_product(user, product):
    return OrderProdukItem.objects.filter(user=user, produk_item=product, ordered=True).exists()
    
def add_review(request, slug):
    produk = get_object_or_404(ProdukItem, slug=slug)
    if has_purchased_product(request.user, produk):
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.produk = produk
                review.user = request.user
                review.save()
                messages.success(request, 'Review telah ditambahkan!')
                return redirect('toko:produk-detail', slug=slug)
        else:
            form = ReviewForm()
        return render(request, 'add_review.html', {'form': form, 'produk': produk})
    else:
        messages.error(request, 'Anda harus membeli produk ini untuk memberikan review.')
        return redirect('toko:produk-detail', slug=slug)
    
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

class PilihAlamatView(LoginRequiredMixin, generic.View):
    def post(self, request, pk, *args, **kwargs):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        # Mengambil ID dari alamat
        request.session['selected_address'] = {
            'address_id': address.pk,
            'nama_penerima': address.nama_penerima,
            'provinsi': address.provinsi.name,
            'kabupaten': address.kabupaten.name,
            'kecamatan': address.kecamatan.name,
            'kelurahan': address.kelurahan.name,
            'kode_pos': address.kode_pos,
            'detail': address.detail
        }
        return redirect('toko:checkout')
    
    
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
                messages.warning(self.request, 'Belum ada belanjaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belanjaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        # Get the user's addresses
        addresses = Address.objects.filter(user=self.request.user)
        selected_address = self.request.session.get('selected_address', None)

        origin = '154'  # ID Kota Asal
        destination = '78'  # ID Kota Tujuan
        weight = 1700  # Berat Barang dalam gram
        couriers = ['jne', 'pos', 'tiki']  # Daftar kurir

        shipping_costs = []
        for courier in couriers:
            cost_data = get_shipping_cost(origin, destination, weight, courier)
            if cost_data['rajaongkir']['status']['code'] == 200:
                for result in cost_data['rajaongkir']['results']:
                    for service in result['costs']:
                        shipping_costs.append({
                            'courier': result['name'],
                            'service': service['service'],
                            'cost': service['cost'][0]['value'],
                            'etd': service['cost'][0]['etd']
                        })
            
        # Store shipping costs in session
        self.request.session['shipping_costs'] = shipping_costs

        context = {
            'form': form,
            'keranjang': order,
            'addresses': addresses,
            'selected_address': selected_address,
            'shipping_costs': shipping_costs
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

class CheckoutView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        order = get_object_or_404(Order, user=self.request.user, ordered=False)

        # Handle Insecure direct object reference
        if order.user != self.request.user:
            raise PermissionDenied('You are not authorized to access this order.')

        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.produk_items.count() == 0:
                messages.warning(self.request, 'Belum ada belanjaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belanjaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        # Get the user's addresses
        addresses = Address.objects.filter(user=self.request.user)
        selected_address = self.request.session.get('selected_address', None)

        origin = '154'  # ID Kota Asal
        destination = '78'  # ID Kota Tujuan
        weight = 1700  # Berat Barang dalam gram
        couriers = ['jne', 'pos', 'tiki']  # Daftar kurir

        shipping_costs = []
        for courier in couriers:
            cost_data = get_shipping_cost(origin, destination, weight, courier)
            if cost_data['rajaongkir']['status']['code'] == 200:
                for result in cost_data['rajaongkir']['results']:
                    for service in result['costs']:
                        shipping_costs.append({
                            'courier': result['name'],
                            'service': service['service'],
                            'cost': service['cost'][0]['value'],
                            'etd': service['cost'][0]['etd']
                        })

        # Store shipping costs in session
        self.request.session['shipping_costs'] = shipping_costs

        context = {
            'form': form,
            'keranjang': order,
            'addresses': addresses,
            'selected_address': selected_address,
            'shipping_costs': shipping_costs
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            shipping_costs = self.request.session.get('shipping_costs', [])  # Retrieve shipping costs from session

            if form.is_valid():
                opsi_pembayaran = form.cleaned_data.get('opsi_pembayaran')
                opsi_pengiriman = form.cleaned_data.get('opsi_pengiriman')
                shipping_option = self.request.POST.get('shipping_option')

                if opsi_pengiriman == 'EX' and shipping_option:
                    # Find the selected shipping cost and courier
                    for cost in shipping_costs:
                        if str(cost['cost']) == shipping_option:
                            order.shipping_cost = cost['cost']
                            order.shipping_courier = cost['courier']
                            break
                elif opsi_pengiriman == 'PR':
                    order.shipping_cost = 0
                    order.shipping_courier = 'Kurir Pribadi'
                # Validate opsi_pembayaran to prevent unauthorized payment method selection
                allowed_payment_methods = ['P', 'C', 'T']  # Add the allowed payment method codes

                if opsi_pembayaran not in allowed_payment_methods:
                    raise PermissionDenied('Invalid payment method selected')

                selected_address = self.request.session.get('selected_address', None)
                if selected_address:
                    alamat_pengiriman = AlamatPengiriman(
                        user=self.request.user,
                        detail_alamat=selected_address.get('detail'),
                        provinsi=selected_address.get('provinsi'),
                        kabupaten=selected_address.get('kabupaten'),
                        kecamatan=selected_address.get('kecamatan'),
                        kelurahan=selected_address.get('kelurahan'),
                        kode_pos=selected_address.get('kode_pos'),
                        nama_penerima=selected_address.get('nama_penerima')
                    )
                    alamat_pengiriman.save()
                    order.alamat_pengiriman = alamat_pengiriman
                    order.delivery_method = opsi_pengiriman
                    order.save()

                else:
                    messages.warning(self.request, 'Alamat pengiriman belum dipilih')
                    return redirect('toko:checkout')

                if opsi_pembayaran == 'P':
                    return redirect('toko:payment', payment_method='paypal')
                elif opsi_pembayaran == 'T':
                    return redirect('toko:payment', payment_method='manual')
                else:
                    return redirect('toko:payment', payment_method='COD')
            else:
                print(form.errors)
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
            payment_method = kwargs.get('payment_method', 'paypal')
            
            # Update total price to include shipping cost
            total_price = order.get_total_harga_order() + (order.shipping_cost or 0)
            
            if payment_method == 'paypal':
                paypal_data = {
                    'business': settings.PAYPAL_RECEIVER_EMAIL,
                    'amount': order.get_total_harga_order(),
                    'item_name': f'Pembayaran belajanan order: {order.id}',
                    'invoice': f'{order.id}-{timezone.now().timestamp()}',
                    'currency_code': 'USD',
                    'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
                    'return_url': self.request.build_absolute_uri(reverse('toko:paypal-return')),
                    'cancel_return': self.request.build_absolute_uri(reverse('toko:paypal-cancel')),
                }

                form = PayPalPaymentsForm(initial=paypal_data)
                context = {
                    'paypalform': form,
                    'order': order,
                    'is_paypal': True,
                    'payment_method': payment_method,
                }
                return render(self.request, template_name, context)

            elif payment_method == 'COD':
                payment = Payment()
                payment.user = self.request.user
                payment.amount = order.get_total_harga_order()
                payment.payment_option = 'C'
                payment.charge_id = f'{order.id}-{timezone.now()}'
                payment.timestamp = timezone.now()
                payment.status = 'B'
                payment.save()

                order_produk_item = OrderProdukItem.objects.filter(user=self.request.user, ordered=False)
                order_produk_item.update(ordered=True)

                order.payment = payment
                order.ordered = True
                order.save()

                context = {
                    'order': order,
                    'payment_method': payment_method,
                }
                return render(self.request, template_name, context)

            elif payment_method == 'manual':
                payment = Payment()
                payment.user = self.request.user
                payment.amount = total_price
                payment.payment_option = 'T'
                payment.charge_id = f'{order.id}-{timezone.now()}'
                payment.timestamp = timezone.now()
                payment.status = 'B'
                payment.save()

                order_produk_item = OrderProdukItem.objects.filter(user=self.request.user, ordered=False)
                order_produk_item.update(ordered=True)

                order.payment = payment
                order.ordered = True
                order.save()

                context = {
                    'order': order,
                    'payment_method': payment_method,
                }
                return render(self.request, template_name, context)

            context = {
                'order': order,
                'payment_method': payment_method,
            }
            return render(self.request, template_name, context)

        except ObjectDoesNotExist:
            return redirect('toko:checkout')


@csrf_exempt
def paypal_return(request):
    if request.user.is_authenticated:
        try:
            print('paypal return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'P' # paypal kalai
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



class OrderHistoryView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_staff:  # Check if the user is an admin
            orders = Order.objects.filter(ordered=True).order_by('-tanggal_order')
        else:
            orders = Order.objects.filter(user=request.user, ordered=True).order_by('-tanggal_order')
        
        context = {
            'orders': orders,
        }
        return render(request, 'order_history.html', context)

class OrderDetailView(UserPassesTestMixin, View):
    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)
        context = {
            'order': order,
            'user': request.user,  # Mengirimkan data pengguna ke template
        }
        return render(request, 'order_detail.html', context)

    def is_admin_or_owner(self):
        order = get_object_or_404(Order, pk=self.kwargs['pk'])
        return self.request.user.is_superuser or self.request.user == order.user

    test_func = is_admin_or_owner


class UpdateOrderStatusView(View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        order = get_object_or_404(Order, pk=order_id)
        
        if order.status == 'P':
            order.status = 'S'  # Ubah status dari Pending ke Shipped
        elif order.status == 'S':
            order.status = 'D'  # Ubah status dari Shipped ke Delivered
        
        order.save()
        return redirect('toko:order-detail', pk=order_id) 
    
@staff_member_required
def update_payment_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if order.payment:
        order.payment.status = status
        order.payment.save()
    return redirect('toko:order-history')