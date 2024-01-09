import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import mongo_connect
from collections import defaultdict
# import nest_asyncio
# nest_asyncio.apply()

config = mongo_connect.config

# app key properties:
tg_token = config['tg_token']
gpt_key = config['gpt_key']

# connect to database
collection = mongo_connect.collection

session_openAI = aiohttp.ClientSession()

# run bot
bot = Bot(token=tg_token)
dp = Dispatcher(bot)


# handling msgs
@dp.message_handler(commands=['start'])
async def start_convers(message:types.Message):
    await mongo_connect.create_user(message)
    await message.reply('Welcome to OctoGPT telegram bot! Just type whatever you want to ask')

@dp.message_handler(commands=['clear'])
async def clear_history(message:types.Message):
    user_id = message['from']['id']
    await collection.find_one_and_update({'telegram_id': user_id}, {'$set':{'messages': []}})
    await message.reply('Your dialogue history was deleted')


@dp.message_handler()
async def all_messages(message: types.Message):
    gpt_resp = await GPT_answer(message=message)
    await message.answer(gpt_resp)


async def GPT_answer(message: types.Message):
    history = await mongo_connect.db_load(message)
    if history != 'low balance':
        history.append({'role': 'user', 'content': message['text']})
        headers = {
            'Authorization': f'Bearer {gpt_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'messages': history,
            'model': 'gpt-3.5-turbo',
        }
        async with session_openAI.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                # proxy='http:/',
                # proxy_auth=aiohttp.BasicAuth('user','pass')
        ) as response:
            gpt_data = await response.json()
            print('json GPT response gpt_data>>', gpt_data)
        answer = gpt_data['choices'][0]['message']['content']
        user_update = [message, gpt_data]
        await mongo_connect.db_add(user_update)
    else:
        answer = 'Please top-up balance'
    return answer


if __name__ == '__main__':
    # print(type(await session_openAI))
    executor.start_polling(dp, skip_updates=True)
