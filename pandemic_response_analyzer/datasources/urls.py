from django.contrib import admin
from django.urls import path
from . import views

app_name = 'datasources'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:source_id>/', views.detail, name='detail'),
    path('new/', views.new, name='new'),
]
