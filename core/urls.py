from django.urls import path, include
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.home, name="home"),
    path('checkout/', views.checkout, name='checkout'),
    path('products/', views.products, name='products')
]