import os
from telethon import TelegramClient, types
from telethon.errors import rpcerrorlist
from user_logger import save_logs
from telethon.tl.patched import Message
from asyncio import sleep


async def send_long_caption(
        client: TelegramClient,
        message: Message,
        media,
        target_channel
        ) -> bool:
    sep = '\n'
    caption = message.message.split('\n')
    if len(caption) <= 2:
        sep = ' '
        caption = message.text.split()
    try:
        await client.send_message(target_channel, message=sep.join(caption[:len(caption)//2]), file=media)
        await client.send_message(target_channel, message=sep.join(caption[len(caption)//2:]))
    except Exception as e:
        await save_logs(e)
        return True
    return False


async def sender(client: TelegramClient, message: Message, target_channel: int | str, can_forward: bool = False) -> None:
    if isinstance(message, types.MessageService):
        return
    file = []
    if isinstance(message.media, list):
        message.media.reverse()
        for media in message.media:
            file.append(media if can_forward else await client.download_media(media))
    try:
        if len(file) != 0:
            await client.send_message(target_channel, message=message.message, file=file)
        else:
            file = await client.download_media(message.message)
            if can_forward:
                await client.send_message(target_channel, message=message)
            else:
                await client.send_message(target_channel, message=message.message, file=file)
    except rpcerrorlist.MediaCaptionTooLongError:
        await send_long_caption(client, message, file, target_channel)
    finally:
        if len(file) != 0 and not can_forward:
            for file in file:
                os.remove(file)


async def message_sender(
        client: TelegramClient,
        message: Message,
        target_channel: str,
        ) -> bool:
    can_forward = True
    with_errors = False
    while True:
        try:
            await sender(client, message, target_channel, can_forward)
        except rpcerrorlist.FloodWaitError as err:
            await sleep(err.seconds)
            await client.send_message('me', f'waited for {err.seconds}')
            continue
        except rpcerrorlist.TimedOutError:
            await sleep(1)
            continue
        except rpcerrorlist.ChatForwardsRestrictedError:
            can_forward = False
            await client.send_message('me', 'bypassing chat restrictions')
            continue
        except Exception as err:
            await save_logs(err)
            await client.send_message(
                'me',
                f'I can\'t send to {target_channel} please check your permissions')
            with_errors = True
        await client.send_message('me', f'have been sent message with id: {message.id}')
        await sleep(4)
        break
    return with_errors
