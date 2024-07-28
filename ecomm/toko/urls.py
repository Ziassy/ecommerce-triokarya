from django.urls import path
from . import views

app_name = 'toko'

urlpatterns = [
     path('', views.HomeListView.as_view(), name='home-produk-list'),
     path('profile/', views.ProfileView.as_view(), name='profile'),
     path('carousel/', views.ProductList.as_view(), name='produk-list'),
     path('carousel/search/', views.ProductList.as_view(), name='product_search'),
     path('product/<slug>/', views.ProductDetailView.as_view(), name='produk-detail'),
     path('product/<slug:slug>/review/', views.add_review, name='add_review'),
     path('contact', views.ContactPageView.as_view(), name='contact'),
     path('contact/success/', views.contact_success, name='contact_success'),
     path('about/', views.about_view, name='about'),
     path('checkout/', views.CheckoutView.as_view(), name='checkout'),
     path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
     path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
     path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
     path('empty-order-summary/', views.empty_view_order_summary, name='empty-order-summary'),
     path('payment/<payment_method>', views.PaymentView.as_view(), name='payment'),
     path('paypal-return/', views.paypal_return, name='paypal-return'),
     path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
     path('address/', views.AddressListView.as_view(), name='address_list'),
     path('address/add/', views.AddressView.as_view(), name='address_add'),
     path('address/<int:pk>/edit/', views.AddressView.as_view(), name='address_edit'),
     path('address/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
     path('pilih-alamat/<int:pk>/', views.PilihAlamatView.as_view(), name='pilih_alamat'),
     path('order-history/', views.OrderHistoryView.as_view(), name='order-history'),
     path('order-detail/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
     path('update-order-status/<int:pk>/', views.UpdateOrderStatusView.as_view(), name='update-order-status'),
]
