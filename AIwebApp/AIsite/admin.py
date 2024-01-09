from django.contrib import admin
from .models import *


class UserDataAdmin(admin.ModelAdmin):
    list_display = ('data_user', 'telegram_username','balance', 'subscription')

class ChatAdmin(admin.ModelAdmin):
    list_display = ('chat_owner', 'chat_name', 'chat_slug')


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('parent_chat', 'role', 'content', 'timestamp')
# Register your models here.


admin.site.register(UserData, UserDataAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Messages, MessagesAdmin)
