from telethon import TelegramClient
from telethon import types
from telethon.tl.patched import Message
from config import API_ID, API_HASH
from time import sleep
from pprint import pprint

source_channel = 'savdo'
target_channel = 'testlalala'
client = TelegramClient('session2', API_ID, API_HASH)

async def main():
    await client.start()
    print('started')
    can_t_forward = False
    last_message_from_target = [await client.get_messages(target_channel, limit=1)][0][0]
    last_message_id = last_message_from_target.id
    last_message_peer_id = last_message_from_target.peer_id
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
            while True:
                media = None
                if isinstance(message.media, types.MessageMediaPhoto):
                    print(message.media.photo.file_reference)
                    pprint(message.media.photo.__dict__)
                    media = types.MessageMediaPhoto(photo=message.media.photo.id)
                elif isinstance(message.media, types.MessageMediaDocument):
                    media = types.MessageMediaDocument(message.media.document.id)
                try_message: Message = Message(id=last_message_id+1, message=message.text, media=message.media.document.id)
                try:
                    print('sending')
                    await client.send_message(target_channel, try_message)
                    print('sended')
                except Exception as err:
                    print('second_cycle', err)
                    sleep(1)
                else:
                    print('succesful')
                    break
                return
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
