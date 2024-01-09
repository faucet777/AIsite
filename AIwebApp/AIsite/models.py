import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserData(models.Model):
    data_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    telegram_username = models.CharField(max_length=255, null=True, blank=True)
    telegram_id = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=True, blank=True, default=1000)
    subscription = models.ForeignKey('Product', on_delete=models.PROTECT, blank=True, null=True,)
    is_guest = models.BooleanField(default=True)
    user_ips = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        duser = self.data_user
        if duser:
            return str(self.data_user)
        else:
            return str(self.pk)



class Chat(models.Model):
    chat_owner = models.ForeignKey(UserData, related_name='chatuser', on_delete=models.CASCADE)
    chat_name = models.CharField(max_length=100, default='New Chat')
    chat_slug = models.SlugField(max_length=255, db_index=True, null=True)
    is_guest_chat = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.chat_slug = ''.join(random.choices(string.ascii_lowercase+string.digits, k=15))
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.chat_slug)

    def get_absolute_url(self):
        return reverse('this_chat', kwargs={'chat_slug': self.chat_slug})

class Messages(models.Model):
    parent_chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20)
    content = models.TextField(blank=True)

    def __str__(self):
        return '_'.join([str(self.parent_chat), str(self.timestamp)])


class Product(models.Model):
    product_tag = models.CharField(max_length=32)
    product_name = models.CharField(max_length=50)
    product_price = models.DecimalField(default=249, max_digits=8, decimal_places=2)
    product_description = models.TextField(blank=True)
    chats_limit = models.IntegerField(default=1)
    token_limit = models.IntegerField(default=1000)

    def __str__(self):
        return str(self.product_name)


class Duration(models.Model):
    duration_tag = models.CharField(max_length=4)
    duration_name = models.CharField(max_length=50)
    duration = models.DurationField()

    def __str__(self):
        return str(self.duration_name)


class Payments(models.Model):
    payment_owner = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now=True)
    product_type = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE)
    expiration_period = models.ForeignKey(Duration, related_name='expiration_period', on_delete=models.PROTECT)
    is_fulfilled = models.BooleanField(default=False)
    # Robokassa API referenced
    OutSum = models.DecimalField(null=True, blank=True, default=0.00, max_digits=8, decimal_places=2)
    Description = models.CharField(null=True, blank=True, max_length=99)
    Email = models.EmailField(blank=True, null=True)
    ExpirationDate = models.DateTimeField(blank=True, null=True)
    UserIp = models.GenericIPAddressField(blank=True, null=True)

    def get_absolute_url(self):
        print('>>>mdls get abs url called')
        return reverse('home')

    def __str__(self):
        return str(self.pk)
    # def __init__(self):
    #     super().__init__(self)
    #     if not self.ExpirationDate:
    #         self.ExpirationDate = self.date_created +<<==!! no summ for Datetime self.expiration_period
    #         print('mdls payments expiryDate>>>>', self.ExpirationDate)


class Ticket(models.Model):
    data_user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(null=True, blank=True, max_length=1024)
    question = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
