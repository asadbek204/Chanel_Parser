# from telethon.sync import TelegramClient
# from config import API_ID, API_HASH

# source_channel = 'allalamani'
# target_channel = 'testlalala'

# client = TelegramClient('session_name', API_ID, API_HASH)
# client.start()
# messages = client.iter_messages(source_channel)
# for message in messages:
#     client.send_message(target_channel, message.text)

# client.disconnect()

###############################################################

import asyncio
from telethon import TelegramClient
from telethon import types
from config import API_ID, API_HASH
from pprint import pprint
from time import sleep

source_channel = 'allalamani'
target_channel = 'testlalala'
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    await client.start()
    a = await client.get_messages(source_channel, limit=100000)
    pprint(len(a))
    for message in a[::-1]:
        pprint(message.text)
        if message.text is not None and message.text != '':
            await client.send_message(target_channel, message.text)
        elif isinstance(message, types.Poll):
            print('Poll')
        print()
        sleep(1)

    await client.disconnect()
asyncio.run(main())