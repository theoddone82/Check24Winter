from django.shortcuts import render

# Create your views here.
"""
URL configuration for attemptNumberTwo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('' , views.story, name='homepage'),
    path('shooting_stars/', views.shooting_stars, name='shooting_stars'),
    path('timeline/', views.timeline, name='timeline'),
    path('2022/' , views.story22, name='2022'),
    path('2023/' , views.story23, name='2023'),
    path('2024/' , views.story24, name='2024'),

]
