# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_protect
import re

# Create your views here.
def signup(request):
    if request.method == "POST": 
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if password != confirm_password:
            messages.warning(request, "Konfirmasi password tidak sesuai.")
            return render(request, 'account/signup.html')
        
        # Password validation
        if len(password) < 5 or not re.search('\d', password) or not re.search('[!@#$%^&*]', password):
            messages.error(request, "Kata sandi harus terdiri dari setidaknya 5 karakter dan mengandung setidaknya satu angka dan satu karakter khusus (!@#$%^&*)")
            return render(request, 'account/signup.html')
                          
        try:
            if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
                messages.error(request, "Email atau Nama Pengguna sudah ada. Silakan pilih email atau nama pengguna yang berbeda.")
                return render(request, 'account/signup.html')
        except Exception as e:
            # Log the exception or handle it as needed
            messages.error(request, "Terjadi kesalahan, silakan coba lagi.")
            return render(request, 'account/signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True  # set is_active to True for newly created user
        user.is_superuser = True  # set to True for access permissions
        user.save()

        return redirect('/auth/login/')

    return render(request, "account/signup.html")


@csrf_protect
def handlelogin(request):
    if request.method=="POST":

        username=request.POST['username']
        password=request.POST['password']
        myuser = authenticate(request, username=username, password=password)

        if myuser is not None and myuser.is_active:
            login(request,myuser)
            return redirect('/')

        else:
            messages.error(request,"Username/Password salah.")
            return redirect('/auth/login')

    return render(request,'account/login.html')   

@csrf_protect #Prevention CSRF (Cross-Site Request Forgery)
def handle_logout(request):
    logout(request)
    # Untuk redirect ke page home ( / ) setelah logout
    return redirect('/')