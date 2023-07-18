from telethon import TelegramClient
from telethon import types
from telethon.tl.patched import Message
from config import API_ID, API_HASH
from time import sleep
from os import remove
from pprint import pprint

source_channel = 'savdo'
target_channel = 'testlalala'
client = TelegramClient('session_name', API_ID, API_HASH)

async def main():
    await client.start()
    print('started')
    can_t_forward = False
    last_message_from_target = [await client.get_messages(target_channel, limit=1)][0][0]
    last_message_id = last_message_from_target.id
    a = await client.get_messages(source_channel, limit=10)
    for message in a[::-1]:
        print('start sending...')
        if not (isinstance(message, types.MessageService) or can_t_forward):
            while True:
                try:
                    await client.send_message(target_channel, message)
                except Exception as err:
                    print('first_cycle', err)
                    can_t_forward = True
                    break
                else:
                    last_message_id += 1
                    print('succesful')
                    break
        print(can_t_forward)
        if not isinstance(message, types.MessageService) and can_t_forward:
            print('try sending...')
            media = await client.download_media(message)
            while True:
                try:
                    print('sending')
                    await client.send_file(target_channel, file=media, caption=message.text)
                    print('sended')
                except Exception as err:
                    print('second_cycle', err)
                    sleep(1)
                    break
                else:
                    print('succesful')
                    last_message_id += 1
                    break
            remove(media)
            print('\n', '-'*20)
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
