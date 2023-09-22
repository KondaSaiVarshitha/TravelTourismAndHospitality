from django.contrib import admin
from django.urls import path, include
from . import views
from django.urls import re_path as url

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('about',views.about,name='about'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
    path('destination_list/<str:city_name>', views.destination_list, name='destination_list'),
    path('destination_list/destination_details/<str:city_name>', views.destination_details, name='destination_details'),
    path('destination_details/<str:city_name>', views.destination_details, name='destination_details'),
    path('destination_list/destination_details/pessanger_detail_def/<str:city_name>',views.pessanger_detail_def,name='pessanger_detail_def'),
    path('upcoming_trips', views.upcoming_trips, name='upcoming_trips'),
    path('destination_list/destination_details/pessanger_detail_def/pessanger_detail_def/card_payment', views.card_payment, name='card_payment'),
    path('destination_list/destination_details/pessanger_detail_def/pessanger_detail_def/otp_verification', views.otp_verification, name='otp_verification'),
    path('destination_list/destination_details/pessanger_detail_def/pessanger_detail_def/net_payment', views.net_payment, name='net_payment'),
    url('datachart', views.indexpage, name='Mainpage'),
    url('selectCountry', views.drillDownACountry, name='drillDown'),
    path('password_reset', views.password_reset_request, name="password_reset")

]
