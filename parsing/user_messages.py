from telethon import TelegramClient
from telethon.tl.patched import Message


def get_media_groups(messages: list) -> tuple[list, bool]:
    check = False
    for i, message in enumerate(messages):
        print('for')
        if not message.grouped_id:
            check = True
            continue
        if not isinstance(message.media, list):
            message.media = [message.media]
        for message2 in messages[i + 1:]:
            print('inner for')
            if message.grouped_id == message2.grouped_id:
                if not isinstance(message2.media, list):
                    message.media.append(message2.media)
                else:
                    message.media.extend(message2.media)
                check = False
                if len(message.message) == 0 and len(message2.message) > 0:
                    message.message = message2.message
                messages.remove(message2)
                continue
            check = True
            break
    print('get_media_groups returned')
    return messages, check


async def get_messages(client: TelegramClient, source_channel: str, limit: int, offset_id: int | None = None) -> list[Message]:
    params = {'entity': source_channel, 'limit': limit}
    if offset_id is not None:
        params.update(max_id=offset_id)
    print('client.get_messages')
    messages: list[Message] = await client.get_messages(**params)
    print('get_media_groups from client messages')
    messages, all_group = get_media_groups(messages)
    print('working')
    while len(messages) < limit or not all_group:
        if not messages:
            print('breaking')
            break
        print('getting other messages', len(messages))
        messages.extend(await get_messages(client, source_channel, limit, messages[-1].id))
        print('messages getten')
        messages, all_group = get_media_groups(messages)
        print('new iter')
    print('return')
    return messages
