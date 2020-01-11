from django.contrib import admin
from .models import OrderItem, Order, Item, Payment, Cupon, Address

# Register your models here.

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

make_refund_accepted.description = "Update orders to refund granted"

class AdminOrder(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'cupon',
                    ]
    list_filter = [
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted'
                    ]
    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'cupon'
    ]
    search_fields = [
                    'user__username',
                    'ref_code'
                    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = [
        'user',
        'street_address',
        'apartment_address',
        'zip',
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, AdminOrder)
admin.site.register(Payment)
admin.site.register(Cupon)
admin.site.register(Address, AddressAdmin)