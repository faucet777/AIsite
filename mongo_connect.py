import motor.motor_asyncio as aiomotor
import datetime
from aiogram import types

config = {
    'db_host': 'localhost',
    'db_port': 27149,
    'default_db': 'test_db',
    'default_collection': 'test_collection',
    'tg_token': '*',
    'gpt_key': '*',
}

# app key properties:
host = config['db_host']
port = config['db_port']
db_name = config['default_db']
cllctn_name = config['default_collection']

# connect to database
db_client = aiomotor.AsyncIOMotorClient(host, port)
db = db_client[db_name]
collection = db[cllctn_name]


async def db_add(update: list[types.Message, dict]):
    user_message = update[0]
    gpt_answer = update[1]['choices'][0]['message']
    token_usage = update[1]['usage']['total_tokens']
    await collection.find_one_and_update({'user_id': user_message['from']['id']},
                                         {'$push': {'messages': {
                                             '$each': [{'role': 'user', 'content': user_message['text']}, gpt_answer]}},
                                          '$inc': {'finances.balance': -token_usage}
                                          }
                                         )


async def db_load(message: types.Message):
    user_id = message['from']['id']
    user_data = await collection.find_one({'telegram_id': user_id})
    if user_data:
        if user_data['finances']['balance'] < 100:
            return 'low balance'

    else:
        await create_user(message)
        return []
    return user_data['messages']


async def create_user(message: [types.Message, dict]):
    if isinstance(message, types.Message):
        await collection.insert_one({
            'pk': None,
            'web_username': None,
            'email': None,
            'telegram_id': message['from']['id'],
            'messages': [],
            'user_data': {
                'first_name': message['from']['first_name'],
                'last_name': message['from']['last_name'],
                'telegram_username': message['from']['username'],
                'language_code': message['from']['username'],
                'registered': datetime.datetime.now(),
            },
            'finances': {
                'balance': 1000,
                'payments': [{
                    'date': None,
                    'ammount': None,
                    'payment_merch': None,
                }]
            },
        })
    elif isinstance(message, dict):
        await collection.insert_one({
            'pk': message['pk'],
            'web_username': message['username'],
            'email': message['email'],
            'telegram_id': None,
            'messages': [],
            'user_data': {
                'first_name': None,
                'last_name': None,
                'telegram_username': None,
                'language_code': None,
                'registered': datetime.datetime.now(),
            },
            'finances': {
                'balance': message['balance'],
                'payments': [{
                    'date': None,
                    'ammount': None,
                    'payment_merch': None,
                }]
            },
        })



