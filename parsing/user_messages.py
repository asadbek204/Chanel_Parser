from telethon import TelegramClient
from telethon.tl.patched import Message


def get_media_groups(messages: list) -> tuple[list, bool]:
    check = False
    for i, message in enumerate(messages):
        print("for")
        if not message.grouped_id:
            check = True
            continue
        if not isinstance(message.media, list):
            message.media = [message.media]
        for message2 in messages[i + 1:]:
            print("inner for")
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
    print("get_media_groups returned")
    return messages, check


async def get_messages(
    client: TelegramClient,
    source_channel: str,
    limit: int,
    offset_id: int | None = None,
) -> list[Message]:
    params = {"entity": source_channel, "limit": limit}
    if offset_id is not None:
        params.update(max_id=offset_id)
    messages: list[Message] = await client.get_messages(**params)
    messages, all_group = get_media_groups(messages)
    length = len(messages)
    while length < limit or not all_group:
        if not messages:
            break
        messages.extend(
            await get_messages(client, source_channel, limit, messages[-1].id)
        )
        messages, all_group = get_media_groups(messages)
        if length == len(messages):
            break
    return messages


async def get_message(
    client: TelegramClient, source_channel: str, message_ids: list[int]
):
    print(messages := await client.get_messages(source_channel, ids=message_ids))
    return messages
