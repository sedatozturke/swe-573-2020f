from django.contrib import admin
from django.urls import path
from . import views

app_name = 'crawler'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:crawl_id>/', views.detail, name='detail'),
    path('new/', views.new, name='new'),
]
