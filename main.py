import asyncio
from telethon import TelegramClient
from telethon import types
from config import API_ID, API_HASH
from time import sleep

source_channel = 'sizbilannnn'
target_channel = 'testlalala'
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    await client.start()
    a = await client.get_messages(source_channel, limit=100000)
    for message in a[::-1]:
        if not isinstance(message, types.MessageService):
            while True:
                try:
                    await client.send_message(target_channel, message)
                except:
                    sleep(1)
                else:
                    break
    await client.disconnect()
asyncio.run(main())
