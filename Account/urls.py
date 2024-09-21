from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import path
from .views import MyPage, userDelete

# Create your views here.
app_name="Account"
urlpatterns = [
    path('myPage/',MyPage.as_view(), name = "mypage"),
    path('delete_success/', userDelete, name="delete_success"),
]