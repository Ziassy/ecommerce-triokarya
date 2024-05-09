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
    if request.method=="POST": 
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Passwords do not match. Please try again.")
            return render(request,'account/signup.html') 
        
        # Password validation
        if len(password) < 5 or not re.search('\d', password) or not re.search('[!@#$%^&*]', password):
            messages.error(request, "Password must be at least 5 characters and contain at least one number and one special character (!@#$%^&*)")
            return render(request, 'account/signup.html')
                          
        try:
            if User.objects.get(email=email) or User.objects.get(username=username):
                # return HttpResponse("email and username already exist")
                messages.error(request,"Email or Username already exists. Please choose a different email or username")
                return render(request,'account/signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(username,email,password)
        user.is_active=True #yang baru signi[, isactive = false
        user.is_superuser=True #for access permission detail produk
        user.save()
        return redirect('/auth/login/')
    return render(request,"account/signup.html")


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
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')

    return render(request,'account/login.html')   

@csrf_protect #Prevention CSRF (Cross-Site Request Forgery)
def handle_logout(request):
    logout(request)
    # Untuk redirect ke page home ( / ) setelah logout
    return redirect('/')