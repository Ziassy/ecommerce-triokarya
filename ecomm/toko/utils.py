from django.conf import settings
import requests

def get_shipping_cost(origin, destination, weight, courier):
    url = settings.BASE_URL
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'key': settings.SECRET_KEY  # Ganti dengan API Key Anda
    }
    data = {
        'origin': origin,
        'destination': destination,
        'weight': weight,
        'courier': courier
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()
