from telethon import TelegramClient
from telethon import types
from config import API_ID, API_HASH
from time import sleep
from os import remove

source_channel = 'savdo'
target_channel = 'testlalala'
limit = 10
client = TelegramClient('session_name', API_ID, API_HASH)

async def main(source_channel, target_channel, limit):
    await client.start()
    print('started')
    can_t_forward = False
    a = await client.get_messages(source_channel, limit=limit)
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
                    print('succesful')
                    break
        print(can_t_forward)
        if not isinstance(message, types.MessageService) and can_t_forward:
            print('try sending...')
            media = None
            if not message.media is None:
                media = await client.download_media(message)
            while True:
                try:
                    print('sending')
                    if not media is None:
                        await client.send_file(target_channel, file=media, caption=message.text)
                    else:
                        await client.send_message(target_channel, message=message.text)
                    print('sended')
                except Exception as err:
                    print('second_cycle', err)
                    sleep(1)
                    break
                else:
                    print('succesful')
                    break
            remove(media)
            print('\n', '-'*20)
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main(source_channel=source_channel, target_channel=target_channel, limit=limit))
