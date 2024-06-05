import time

from asyncio import sleep
from .user_messages import get_messages, get_message
from .send_message import message_sender

from telethon import TelegramClient
from telethon.errors import rpcerrorlist


async def copy_messages_from_channel(
        client: TelegramClient,
        source_channel: int | str,
        target_channel: int | str,
        limit: int = 1
        ) -> None:
    try:
        source_channel = int(source_channel)
    except ValueError:
        ...
    try:
        target_channel = int(target_channel)
    except ValueError:
        ...
    start_time = time.time()
    async with client as client:
        try:
            await client.send_message('me', f'started from {source_channel} to {target_channel}')
        except rpcerrorlist.FloodWaitError as err:
            print(err.seconds)
            await sleep(err.seconds)
            await client.send_message('me', f'waited for {err.seconds}')
        try:
            messages = await get_messages(client, source_channel, limit)
            messages = messages[:limit]
            messages.reverse()
            result = False
            for message in messages:
                result = not await message_sender(client, message, target_channel)
            if result:
                await client.send_message(
                    'me',
                    f'finished copy from {source_channel} to {target_channel} successfully ({"%.2f" % (time.time() - start_time)}s)')
                return
            await client.send_message('me', f'finished copy from {source_channel} to {target_channel} with error')
        except rpcerrorlist.UsernameInvalidError:
            await client.send_message('me', 'invalid username for one of channel please try again!')


async def copy_by_id(
        client: TelegramClient,
        source_channel: str | int,
        target_channel: str | int,
        ids: list[int]
    ):
    try:
        source_channel = int(source_channel)
    except ValueError:
        ...
    try:
        target_channel = int(target_channel)
    except ValueError:
        ...
    start_time = time.time()
    async with client as client:
        try:
            await client.send_message('me', f'started from {source_channel} to {target_channel}')
        except rpcerrorlist.FloodWaitError as err:
            print(err.seconds)
            await sleep(err.seconds)
            await client.send_message('me', f'waited for {err.seconds}')
        try:
            messages = await get_message(client, source_channel, ids)
            for message in messages:
                result = not await message_sender(client, message, target_channel)
            if result:
                await client.send_message(
                    'me',
                    f'finished copy from {source_channel} to {target_channel} successfully ({"%.2f" % (time.time() - start_time)}s)')
                return
            await client.send_message('me', f'finished copy from {source_channel} to {target_channel} with error')
        except rpcerrorlist.UsernameInvalidError:
            await client.send_message('me', 'invalid username for one of channel please try again!')