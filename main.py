from telethon import TelegramClient
from telethon import types
from telethon.tl.custom import Message
from telethon.errors import rpcerrorlist
from config import API_ID, API_HASH
from time import sleep
from os import remove

async def main(client: TelegramClient, source_channel, target_channel, start):
    await client.start()
    print('started')
    can_t_forward = False
    messages = (await client.get_messages(source_channel, limit=start))
    for message in messages[::-1]:
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
                print('\n', '-'*20, '\n')
                continue
        if not isinstance(message, types.MessageService) and can_t_forward:
            print('try sending...')
            media = await Message.download_media(message)
            try:
                await client.send_message(target_channel, message=message.text, file=media)
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
    start = 3
    source_channel = 'savdo'
    target_channel = 'testlalala'
    client = TelegramClient('session_name', API_ID, API_HASH)
    asyncio.run(main(client=client, source_channel=source_channel, target_channel=target_channel, start=start))
