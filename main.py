from telethon import TelegramClient
from telethon import types, helpers
from telethon.tl.custom import Message
from telethon.errors import rpcerrorlist
from config import API_ID, API_HASH
from time import sleep
from os import remove

async def main(client: TelegramClient, source_channel, target_channel, limit):
    await client.start()
    print('started')
    can_t_forward = False
    messages = await client.get_messages(source_channel, limit=limit)
    for message in messages[::-1]:
        print('start sending...')
        if not (isinstance(message, types.MessageService) or can_t_forward):
            try:
                await client.send_message(target_channel, message)
            except rpcerrorlist.ChatForwardsRestrictedError as err:
                print(err)
                can_t_forward = True
            except rpcerrorlist.MediaCaptionTooLongError as err:
                print(err)
                caption = message.text.split('\n')
                try:
                    await client.send_message(target_channel, message='\n'.join(caption[:len(caption)//2]), file=message.media)
                    await client.send_message(target_channel, message='\n'.join(caption[len(caption)//2:]))
                except:
                    print('going to next_try')
                    can_t_forward = True
                else:
                    print('succesful')
            except Exception as err:
                print(f'first_cycle type(err):{type(err)}\n', err)
            else:
                print('succesful')
        if not isinstance(message, types.MessageService) and can_t_forward:
            print('try sending...')
            media = await Message.download_media(message)
            try:
                print('sending')
                await client.send_message(target_channel, message=message.text, file=media)
                print('sended')
            except rpcerrorlist.MediaCaptionTooLongError as err:
                print(err)
                caption = message.text.split('\n')
                try:
                    await client.send_message(target_channel, message='\n'.join(caption[:len(caption)//2]), file=media)
                    await client.send_message(target_channel, message='\n'.join(caption[len(caption)//2:]))
                except Exception as err:
                    print(f'second_cycle::second_try type(err):{type(err)}', err)
                else:
                    print('succesful')
            except Exception as err:
                print(f'second_cycle type(err):{type(err)}\n', err)
                sleep(1)
            else:
                print('succesful')
            finally:
                if not media is None:
                    print(f'cleaning... {media}')
                    remove(media)
                    print('cleaned!!!')
        print('\n', '-'*20, '\n')
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    source_channel = 'savdo'
    target_channel = 'testlalala'
    limit = 10
    client = TelegramClient('session_name', API_ID, API_HASH)
    asyncio.run(main(client=client, source_channel=source_channel, target_channel=target_channel, limit=limit))
