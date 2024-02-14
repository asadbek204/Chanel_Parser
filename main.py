from telethon import TelegramClient
from telethon import types
from telethon.errors import rpcerrorlist
from telethon.tl.custom import Message
from time import sleep
from os import remove


async def send_long_caption(client: TelegramClient, message, media, target_channel):
    sep = '\n'
    caption = message.text.split('\n')
    if len(caption) <= 2:
        sep = ' '
        caption = message.text.split()
    try:
        await client.send_message(target_channel, message=sep.join(caption[:len(caption)//2]), file=media)
        await client.send_message(target_channel, message=sep.join(caption[len(caption)//2:]))
    except Exception as e:
        print("sending long caption error", e)
        return True
    else:
        return False


async def copy_messages_from_channel(client: TelegramClient, source_channel: int | str, target_channel: int | str, limit: int = 1):
    async with client as client:
        try:
            await client.send_message('me', f'started from {source_channel} to {target_channel}')
        except rpcerrorlist.FloodWaitError:
            pass
        can_t_forward = False
        messages = await client.get_messages(source_channel, limit=limit)
        for message in messages[::-1]:
            while True:
                if not (isinstance(message, types.MessageService) or can_t_forward):
                    try:
                        await client.send_message(target_channel, message)
                    except rpcerrorlist.ChatForwardsRestrictedError as err:
                        await client.send_message('me', str(err))
                        can_t_forward = True
                        continue
                    except rpcerrorlist.MediaCaptionTooLongError:
                        can_t_forward = await send_long_caption(client, message, message.media, target_channel)
                        continue
                    except rpcerrorlist.FloodWaitError as err:
                        print(f'sleep for: {err.seconds} seconds')
                        sleep(err.seconds)
                        continue
                if not isinstance(message, types.MessageService) and can_t_forward:
                    media = await Message.download_media(message)
                    file = await client.upload_file(media)
                    try:
                        await client.send_message(target_channel, message=message.text, file=file)
                    except rpcerrorlist.MediaCaptionTooLongError:
                        await send_long_caption(client, message, file, target_channel)
                        continue
                    except rpcerrorlist.FloodWaitError as err:
                        print(f'sleep for: {err.seconds} seconds')
                        sleep(err.seconds)
                        continue
                    else:
                        if media is not None:
                            remove(media)
                        print('\n', '-'*20, '\n')
                sleep(4)
                break
        await client.send_message('me', f'finished copy from {source_channel} to {target_channel}')
