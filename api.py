from fastapi import FastAPI, BackgroundTasks, HTTPException
from telethon.errors import rpcerrorlist
from telethon import TelegramClient
from main import copy_messages_from_channel
from config import API_ID, API_HASH
from hashlib import sha256
import json

app = FastAPI(title="Channel Parser")
sessions: dict[str, dict] = {}
sessions_file_name = 'sessions.json'


async def get_client(username: str, password: str) -> TelegramClient:
    client = sessions.get(username, False)
    if not client:
        raise HTTPException(status_code=404, detail="client not found")
    if sha256(password.encode()).hexdigest() != client.get('password'):
        raise HTTPException(status_code=401, detail="invalid password")
    return TelegramClient(client.get('session_name'), API_ID, API_HASH)


@app.post('/parse_channel')
async def parse_channel(
        background_tasks: BackgroundTasks,
        username: str,
        password: str,
        src_channel: int | str,
        target_channel: int | str,
        limit: int | None = None
        ):
    client = await get_client(username, password)
    background_tasks.add_task(copy_messages_from_channel, client, src_channel, target_channel, limit)
    return {'status': 'success', 'message': 'started copying messages'}


@app.post('/account/authorization')
async def authorization(username: str, password: str, phone: str):
    session_name = f'sessions/{username}'
    if username in sessions:
        raise HTTPException(status_code=409, detail="this username already exists")
    try:
        client = TelegramClient(session_name, API_ID, API_HASH)
        await client.connect()
        phone_code_hash = (await client.send_code_request(phone=phone)).phone_code_hash
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    sessions[username] = {'password': sha256(password.encode()).hexdigest(), 'session_name': session_name, 'phone_code_hash': phone_code_hash}
    print(sessions[username])
    await client.disconnect()
    return {'status': 'success', 'message': 'authorization successful, send verification code to sign_in'}


@app.post('/account/sign_in')
async def sign_in(username: str, password: str, phone: str, verification_code: str, two_factor_auth_password: str | None = None):
    client = await get_client(username, password)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=verification_code, phone_code_hash=sessions[username]['phone_code_hash'])
    except rpcerrorlist.SessionPasswordNeededError:
        try:
            await client.sign_in(password=two_factor_auth_password)
        except rpcerrorlist.SessionPasswordNeededError as err:
            raise HTTPException(status_code=404, detail=str(err))
    await client.disconnect()
    return {'status': 'success', 'message': 'sign in successful'}


@app.get('/account')
async def get_account(username: str, password: str):
    client = await get_client(username, password)
    return {'status': 'success', 'message': 'account successfully found', 'detail': client}


@app.on_event('startup')
async def startup():
    global sessions
    try:
        sessions = json.load(open(sessions_file_name))
    except json.decoder.JSONDecodeError:
        sessions = {}
    except FileNotFoundError:
        with open(sessions_file_name, 'x') as created:
            created.write(json.dumps(sessions))


@app.on_event('shutdown')
async def shutdown():
    json.dump(sessions, open(sessions_file_name, 'w'))
