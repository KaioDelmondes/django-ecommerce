from django.contrib import admin
from .models import OrderItem, Order, Item, Payment, Cupon

# Register your models here.

class AdminOrder(admin.ModelAdmin):
    list_display = ['user', 'ordered']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, AdminOrder)
admin.site.register(Payment)
admin.site.register(Cupon)
