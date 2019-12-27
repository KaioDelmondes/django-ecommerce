from django.shortcuts import render
from .models import Item

# Create your views here.

def home(request):
    return render(request, "test-home-page.html")

def checkout(request):
    return render(request, 'test-checkout-page.html')

def products(request):
    return render(request, 'test-product-page.html')