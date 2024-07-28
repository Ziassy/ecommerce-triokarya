from django import template
from toko.models import Order
from django.utils.timezone import localtime
import pytz

register = template.Library()

@register.filter
def total_produk_dikeranjang(user):
    if user.is_authenticated:
        query = Order.objects.filter(user=user, ordered=False)
        if query.exists():
            return query[0].produk_items.count()
    return 0

@register.filter(name='convert_to_wib')
def convert_to_wib(value):
    # Convert the time to WIB timezone
    jakarta_timezone = pytz.timezone('Asia/Jakarta')
    localized_time = value.astimezone(jakarta_timezone)
    return localized_time.strftime('%d-%m-%Y %H:%M:%S %Z')

@register.filter
def currency_idr(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value  # Return the original value if conversion fails

    return "Rp {:,.0f}".format(value).replace(',', '.')