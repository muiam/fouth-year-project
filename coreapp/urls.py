from django.urls import path
from . import views

urlpatterns=[
    path('', views.homepage, name='home'),
    path('login/', views.login, name='login'),
    path('checkmail', views.checkmail, name='checkmail'),
    path('accountlogin', views.accountlogin, name='accountlogin'),
    path('logoutuser', views.logoutuser, name='logout'),
    path('project/<str:pk>/', views.projectdetails, name='project'),
    path('payment/<str:pk>/', views.payment, name='payment'),
    path('pay',views.pay, name='pay'),
    path('callback/<str:pk>/',views.callback, name='callback'),
    path('userrequests/',views.userrequests, name='userrequests'),
    path('userpurchases/',views.userpurchases, name='userpurchases')







]