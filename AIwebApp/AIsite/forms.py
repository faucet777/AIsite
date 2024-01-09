from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from AIsite.models import Payments, Product, Duration, Ticket
import AIsite.robokassa as kassa
from AIwebApp.settings import MERCHANT_LOGIN, MERCHANT_PASS1, MERCHANT_PASS2

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-input'}), max_length=128)
    email = forms.EmailField(label='Электронная почта', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-input'}), max_length=128)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class PaymentForm(ModelForm):
    product_type = forms.ModelChoiceField(queryset=Product.objects.all().exclude(product_tag='FREE').exclude(product_tag='GUEST'), to_field_name='product_name', empty_label='план не выбран', label='Выберите ваш план')
    expiration_period = forms.ModelChoiceField(queryset=Duration.objects.all(), empty_label='период не выбран', label='Период подписки')

    def prod_info(self):
        return [(prod.product_name, prod.product_description) for prod in self.fields['product_type']._queryset]

    def get_payment_link(self):
        self.save()
        return kassa.generate_payment_link(
            merchant_login=MERCHANT_LOGIN,  # Merchant login
            merchant_password_1=MERCHANT_PASS1,  # Merchant password
            cost=self.instance.OutSum,  # Cost of goods, RU
            number=self.instance.pk,  # Invoice number
            description=self.instance.Description,  # Description of the purchase
            is_test=1,
            robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
        )

    class Meta:
        model = Payments
        fields = ('product_type', 'expiration_period')


class SupportForm(ModelForm):
    subject = forms.CharField(label='Тема обращения', max_length=255, widget=forms.TextInput(attrs={'class': 'form-input'}))
    question = forms.CharField(label='Ваше обращение', max_length=2048, widget=forms.Textarea(attrs={'class': 'form-input','rows':10, 'cols':60}))
    contact_email = forms.EmailField(label='Электронная почта', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Ticket
        fields = ('subject', 'question', 'contact_email')

