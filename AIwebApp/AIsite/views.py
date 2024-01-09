import datetime
import os

from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView

from AIwebApp import settings
from .forms import *
from .utils import DataMixin
from .models import *
from AIwebApp.settings import MERCHANT_LOGIN, MERCHANT_PASS1, MERCHANT_PASS2
import AIsite.robokassa as kassa


class ChatAreaView(DataMixin, TemplateView):
    template_name = 'AIsite/chat.html'

    def get_context_data(self, chat_slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items()) + list(c_def.items()))
        duser = context['data_user']

        if chat_slug is not None:
            context['chat_selected'] = chat_slug
            chats = Chat.objects.filter(chat_owner=duser)
            chat = Chat.objects.get(chat_slug=chat_slug)
            self.request.session['cur_chat'] = chat_slug
            print('vws chatview sesion', self.request.session['cur_chat'])
            msg_history = Messages.objects.filter(parent_chat=chat)
            context['aside_data'] = [chat for chat in chats if chat.is_guest_chat == duser.is_guest]
            context['msg_history'] = msg_history
        else:
            self.request.session['cur_chat'] = 'not_defined'
            try:
                chats = Chat.objects.filter(chat_owner=duser)
                context['aside_data'] = [chat for chat in chats if chat.is_guest_chat == duser.is_guest]
                context['msg_history'] = None

            except Exception as e:
                newchat = Chat.objects.create(data_user=duser)
                return redirect('this_chat', newchat.chat_slug)
        return context

class ChatAreaLobby(DataMixin, TemplateView):
    template_name = 'AIsite/chat_lobby.html'

    def get_context_data(self, chat_slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items()) + list(c_def.items()))
        duser = context['data_user']
        chats = Chat.objects.filter(chat_owner=duser)
        if chats:
            context['aside_data'] = [chat for chat in chats if chat.is_guest_chat == duser.is_guest]
            context['msg_history'] = None

        context['chat_selected'] = 0
        return context



class RegisterPage(DataMixin, CreateView):
    template_name = 'AIsite/register.html'
    form_class = RegisterUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy('lk')
        else:
            return reverse_lazy('login')


class LoginPage(DataMixin, LoginView):
    form_class = LoginForm
    template_name = 'AIsite/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse_lazy('chat')
        else:
            return reverse_lazy('login')


class ResetPage(DataMixin, PasswordResetView):
    template_name = 'AIsite/reset.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class ResetDonePage(DataMixin, PasswordResetDoneView):
    template_name = 'AIsite/reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class ResetConfirmPage(DataMixin, PasswordResetConfirmView):
    template_name = 'AIsite/reset_confirm.html'
    post_reset_login = True
    success_url = reverse_lazy('lk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class ResetCompletePage(DataMixin, PasswordResetCompleteView):
    template_name = 'AIsite/reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class AccountPage(LoginRequiredMixin, DataMixin, FormView):
    template_name = 'AIsite/lk.html'
    form_class = PaymentForm
    # success_url = reverse_lazy('paydone')

    def make_payment(self, form: PaymentForm):
        user = self.request.user
        ud = UserData.objects.get(data_user=user)
        email = user.email
        form.instance.payment_owner = ud
        form.instance.OutSum = round(form.cleaned_data['expiration_period'].duration.days / 30) * float(form.cleaned_data['product_type'].product_price)
        form.instance.Description = form.cleaned_data['product_type'].product_name
        form.instance.Email = email
        form.instance.ExpirationDate = datetime.datetime.now() + datetime.timedelta(days=3)
        form.instance.UserIp = self.request.META['REMOTE_ADDR']
        return form

    def form_valid(self, form):
        form_upd = self.make_payment(form=form)
        payment_link = form_upd.get_payment_link()
        return HttpResponseRedirect(payment_link)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context['form'] = self.form_class
        context = dict(list(context.items())+list(c_def.items()))
        context['products'] = Product.objects.exclude(product_tag='FREE').exclude(product_tag='GUEST')
        return context


class PaymentDonePage(DataMixin, TemplateView):
    template_name = 'AIsite/payment_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context

class PaymentFailPage(DataMixin, TemplateView):
    template_name = 'AIsite/payment_fail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class MainPage(DataMixin, TemplateView):
    template_name = 'AIsite/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items())+list(c_def.items()))
        return context


class SupportPage(DataMixin, CreateView):
    template_name = 'AIsite/support.html'
    form_class = SupportForm
    success_url = reverse_lazy('support')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context()
        context = dict(list(context.items()) + list(c_def.items()))
        context['form'] = self.form_class
        return context

    # def get_success_url(self):
    #     return reverse_lazy('support')


def delete_chat(request, chat_slug):
    Chat.objects.get(chat_slug=chat_slug).delete()
    return redirect('chat')

def logout_user(request):
    logout(request)
    return redirect('login')



def merchant_confirmation_endpoint(request):
    if request.method == 'GET':
        print('>>>>>>>>>>vws request result', str(request.GET))
        with open('pay_log.log', 'a+') as plog:
            plog.write(str(request.GET) +'\n')
        res = kassa.result_payment(MERCHANT_PASS2, request)
        if res[0]:
            inv_id = res[1]['InvId']
            bill = Payments.objects.get(pk=inv_id)
            bill.is_fulfilled = True
            bill.save()
            udata = bill.payment_owner
            udata.subscription = bill.product_type
            udata.balance += bill.product_type.token_limit
            udata.save()
            return f'OK{inv_id}'
        else:
            return 'bad sign'

    else:
        return '405:MethodNotAllowed'


def exeption404(request, exception):
    return render(request, 'page404.html')

# def download(request, path):
#     file_path = os.path.join(settings.MEDIA_ROOT, path)
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
#             return response
#     raise Http404