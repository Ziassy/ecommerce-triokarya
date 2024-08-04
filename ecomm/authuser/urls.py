from django.urls import path
from authuser import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.handlelogin, name='handlelogin'),
    path('login/', views.login, name='login'),
]
