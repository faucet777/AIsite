import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
from .utils import gpt_answer


@sync_to_async()
def load_msgs(chat_slug):
    chat = Chat.objects.get(chat_slug=chat_slug)
    mgs = Messages.objects.filter(parent_chat=chat)
    mgs_list = []
    for mg in mgs:
        role = mg.role
        content = mg.content
        mgd = dict(role=role, content=content)
        mgs_list.append(mgd)
    return mgs_list


@sync_to_async()
def create_msg(chat_slug, role, message):
    chat = Chat.objects.get(chat_slug=chat_slug)
    m = Messages(parent_chat=chat, role=role, content=message)
    m.save()
    return


@sync_to_async()
def make_answer(mesgs):
    answer = gpt_answer(mesgs)
    return answer


@sync_to_async()
def create_new_chat(usr_pk, chat_name:str='New Chat'):
    usr = UserData.objects.get(pk=usr_pk)
    if usr.is_guest:
        if Chat.objects.filter(chat_owner=usr, is_guest_chat=1).count() >= 1:
            return 'chat_limit'
        else:
            Chat.objects.create(chat_owner=usr, chat_name=chat_name, is_guest_chat=usr.is_guest)
            return 'chat_created'
    else:
        if Chat.objects.filter(chat_owner=usr).count() >= usr.subscription.chats_limit:
            return 'chat_limit'
        else:
            Chat.objects.create(chat_owner=usr, chat_name=chat_name, is_guest_chat=usr.is_guest)
            return 'chat_created'


@sync_to_async()
def update_balance(token_usage:int, user_pk):
    user = UserData.objects.get(pk=user_pk)
    user.balance -= token_usage
    user.save()
    return user.balance
@sync_to_async()
def cur_balance(duser_pk):
    user = UserData.objects.get(pk=duser_pk)
    if user.balance <= 300:
        return False
    else:
        return True

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        type = data['type']
        event_data = data['event_data']
        await self.channel_layer.send(message={
            'type': type,
            'event_data': event_data,
        }, channel=self.channel_name)

    async def chat_message(self, event):
        if await cur_balance(self.scope['session']['user_pk']):
            data = event['event_data']
            chat_slug = self.scope['session']['cur_chat']
            if chat_slug != 'not_defined':
                await create_msg(chat_slug, 'user', event['event_data']['message'])  # save new msg to db
                await self.send(text_data=json.dumps(                             # send your message back to frontend to add in DOM
                    {'type': 'chat.message',
                     'event_data': data,
                     }
                ))
                msgs = await load_msgs(chat_slug)  # load mesgs history from db
                resp = await make_answer(msgs)  # get gpt answer
                answer = resp[0]
                tokens_used = resp[1]
                await update_balance(tokens_used, self.scope['session']['user_pk'])

                await self.send(text_data=json.dumps(
                    {'type': 'chat.message',
                     'event_data': {
                         'sender': 'OctoGPT',
                         'message': answer
                     },
                     }
                ))
                await create_msg(chat_slug, 'assistant', answer)  # save answer to db
        else:
            await self.send(text_data=json.dumps(
                {'type': 'token.limit',
                 'event_data': {
                     'sender': 'OctoGPT',
                     'message': 'Закончились токены, улучшите ваш тарифный план в личном кабинете или дождитесь даты обновления лимита'
                 },
                 }
            ))


    async def chat_create(self, event):
        chat_name_new = event['event_data']
        creation_result = await create_new_chat(self.scope['session']['user_pk'], chat_name_new)
        await self.send(text_data=json.dumps(
            {'type': 'chat.create',
             'event_data': creation_result,
             }
        ))
