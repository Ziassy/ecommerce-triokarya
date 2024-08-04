from django.http import JsonResponse
from .models import Kabupaten, Kecamatan, Kelurahan

def get_kabupaten(request):
    provinsi_id = request.GET.get('provinsi_id')
    kabupaten = Kabupaten.objects.filter(id_provinsi=provinsi_id).values('id', 'name')
    return JsonResponse(list(kabupaten), safe=False)

def get_kecamatan(request):
    kabupaten_id = request.GET.get('kabupaten_id')
    kecamatan = Kecamatan.objects.filter(id_kabupaten=kabupaten_id).values('id', 'name')
    return JsonResponse(list(kecamatan), safe=False)

def get_kelurahan(request):
    kecamatan_id = request.GET.get('kecamatan_id')
    kelurahan = Kelurahan.objects.filter(id_kecamatan=kecamatan_id).values('id', 'name')
    return JsonResponse(list(kelurahan), safe=False)
