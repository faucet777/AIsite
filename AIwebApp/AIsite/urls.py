from django.urls import path, include
from AIsite.views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("account/", AccountPage.as_view(), name='lk'),
    path("account/payment_done/", PaymentDonePage.as_view(), name='paydone'),
    path("account/payment_fail/", PaymentFailPage.as_view(), name='payfail'),
    path("payment_confirm/", merchant_confirmation_endpoint, name='payresult'),
    path("", MainPage.as_view(), name='home'),
    path("register/", RegisterPage.as_view(), name='register'),
    path("login/", LoginPage.as_view(), name='login'),
    path("chat/<slug:chat_slug>/", ChatAreaView.as_view(), name="this_chat"),
    path("logout/", logout_user, name='logout'),
    path("chat/", ChatAreaLobby.as_view(), name="chat"),
    path("delete_chat/<slug:chat_slug>/", delete_chat, name="delete_chat"),
    path("support/", SupportPage.as_view(), name='support'),
    path("reset/", ResetPage.as_view(), name='reset'),
    path("resetdone/", ResetDonePage.as_view(), name='password_reset_done'),
    path("resetdone/<slug:uidb64>/<slug:token>", ResetConfirmPage.as_view(), name='password_reset_confirm'),
    path("resetcomplete/", ResetCompletePage.as_view(), name='password_reset_complete'),

]

handler404 = exeption404