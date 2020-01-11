from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, Order, OrderItem, BillingAddress, Payment, Cupon
from .forms import CheckoutForm, CuponForm

# Create your views here.


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form' : form,
                'order' : order,
                'cuponForm' : CuponForm,
                'DISPLAY_CUPON_FORM': True,
            }
            return render(self.request, 'checkout-page.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")

        
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                #TODO: Add functionality for these fields
                #same_shipping_address = form.cleaned_data.get('same_shipping_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # TODO: Add redirect to the select payment option
                if payment_option == 'S':
                    return redirect("core:payment", payment_option='stripe')
                elif payment_option == 'P':
                    return redirect("core:payment", payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            
            messages.warning(self.request, "Failured to Checkout")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            return redirect('core:order-summary')

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        if order.billing_address:
            context = {
                'order' : order,
                'DISPLAY_CUPON_FORM': False,
            }
            return render(self.request, 'payment.html', context)
        else:
            messages.error(self.request, "You have not added a billing address")
            return redirect('core:checkout')
    
    def post(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
        # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount = amount,
                currency = "usd",
                source = token,
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
        
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "You sucessfull!")
            return redirect("/")

        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authenticaded")
            return redirect("/")
        
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            messages.error(self.request, "Something went wrong. Try again later")
            return redirect("/")

        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "A serious error has occurred. We have been notified.")
            return redirect("/")
       
class HomeView(ListView):
    model = Item
    paginate_by = 1
    template_name = 'home-page.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

class OrderSumaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            context={
                'object': order
                }
            return render(self.request, 'order-sumary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")

def get_cupon(request, code):
    try:
        cupon = Cupon.objects.get(code = code)
        return cupon
    except ObjectDoesNotExist:
        messages.warning(request, "The cupon does not exists")
        redirect('core:order-sumary')

class AddCuponView(View):
    def post(self, *args, **kwargs):
        cupon_form = CuponForm(self.request.POST or None)
        if cupon_form.is_valid():
            code = cupon_form.cleaned_data.get('code')
            cupon = get_cupon(self.request, code)
            try:
                order = Order.objects.get(user = self.request.user, ordered=False)
                order.cupon = cupon
                order.save()
                
                messages.success(self.request, "The cupon was accepted!")
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order")
                return redirect("/")
        else:
            messages.warning(self.request, "This cupon is not valid!")
            return redirect('core:checkout')


@login_required            
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug):
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('core:order-sumary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('core:order-sumary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('core:order-sumary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False
                )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('core:product', slug = slug)
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('core:product', slug = slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:product', slug = slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered = False
                )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect('core:order-sumary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('core:product', slug = slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:product', slug = slug)