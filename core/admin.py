from django.contrib import admin
from .models import OrderItem, Order, Item, Payment, Cupon

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
        'payment',
        'cupon'
    ]
    search_fields = [
                    'user__username',
                    'ref_code'
                    ]
    actions = [make_refund_accepted]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, AdminOrder)
admin.site.register(Payment)
admin.site.register(Cupon)
