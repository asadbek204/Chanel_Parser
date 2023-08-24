from telethon import TelegramClient
from telethon import types
from telethon.errors import rpcerrorlist
from telethon.tl.custom import Message
from config import API_ID, API_HASH
from time import sleep, perf_counter
from os import remove

async def send_long_caption(client: TelegramClient, message, media, err):
    print(err)
    sep = '\n'
    caption = message.text.split('\n')
    if len(caption) <= 2:
        sep = ' '
        caption = message.text.split()
    try:
        await client.send_message(target_channel, message=sep.join(caption[:len(caption)//2]), file=media)
        await client.send_message(target_channel, message=sep.join(caption[len(caption)//2:]))
    except Exception as err:
        print(err)
        return True
    else:
        print('succesful')

async def main(client: TelegramClient, source_channel, target_channel, limit):
    await client.start()
    can_t_forward = False
    try:
        messages = await client.get_messages(source_channel, limit=limit)
    except Exception as err:
        print(err)
    print('started')
    for message in messages[::-1]:
        if not (isinstance(message, types.MessageService) or can_t_forward):
            while True:
                print('sending...')
                try:
                    await client.send_message(target_channel, message)
                except rpcerrorlist.ChatForwardsRestrictedError as err:
                    print(err)
                    can_t_forward = True
                except rpcerrorlist.MediaCaptionTooLongError as err:
                    can_t_forward = await send_long_caption(client, message, message.media, f'first_cycle: {err}')
                except rpcerrorlist.FloodWaitError as err:
                    print(err)
                    sleep(int(str(err).split()[3])/2)
                    continue
                except Exception as err:
                    print(f'first_cycle type(err):{type(err)}\n', err)
                else:
                    print('succesful')
                finally:
                    print('\n', '-'*20, '\n')
                    break
        if not isinstance(message, types.MessageService) and can_t_forward:
            while True:
                print('try sending...')
                media = await Message.download_media(message)
                try:
                    await client.send_message(target_channel, message=message.text, file=media)
                except rpcerrorlist.MediaCaptionTooLongError as err:
                    await send_long_caption(client, message, media, f'second_cycle: {err}')
                except rpcerrorlist.FloodWaitError as err:
                    print(err)
                    sleep(int(str(err).split()[3])/2)
                    continue
                except Exception as err:
                    print(f'second_cycle type(err):{type(err)}\n', err)
                else:
                    print('succesful')
                finally:
                    if not media is None:
                        print(f'cleaning... {media}')
                        remove(media)
                        print('cleaned!!!')
                    print('\n', '-'*20, '\n')
                    break
    print(len(messages))
    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    limit = 10000000
    source_channel = -1001947604230
    target_channel = 'Quramboyevv'
    client = TelegramClient('session_name', API_ID, API_HASH)
    start_time = perf_counter()
    asyncio.run(main(client=client, source_channel=source_channel, target_channel=target_channel, limit=limit))
    end_time = perf_counter()
    print(end_time-start_time)
