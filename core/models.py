from django.db import models
from django.conf import settings

# Create your models here.

class Item(models.Model):
    title = models.CharField(max_length=100)
    prince = models.FloatField()

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField()


    def __str__(self):
        return self.user.username
