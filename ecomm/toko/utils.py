import requests

def get_shipping_cost(origin, destination, weight, courier):
    url = 'https://api.rajaongkir.com/starter/cost'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'key': '2049bc20157892f34b3c0e73f2e93bb0'  # Ganti dengan API Key Anda
    }
    data = {
        'origin': origin,
        'destination': destination,
        'weight': weight,
        'courier': courier
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()
