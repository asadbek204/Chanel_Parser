import os
import json
from contextlib import asynccontextmanager

from telethon.errors import rpcerrorlist
from telethon import TelegramClient
from config import API_ID, API_HASH
from hashlib import sha256
from parsing.parser_app import copy_messages_from_channel, copy_by_id

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Body
# from fastapi_users import FastAPIUsers
# from database.models import User
# from auth.manager import get_user_manager
# from auth.auth import auth_backend
# from auth.schemas import UserRead, UserCreate, UserUpdate


sessions: dict[str, dict] = {}
sessions_file_name = 'sessions.json'

# fastapi_users = FastAPIUsers[User, int](
#     get_user_manager,
#     [auth_backend],
# )
#
# app.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["auth"],
# )
#
# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth/jwt",
#     tags=["auth"],
# )
#
# app.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
#
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
#
# app.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )
#

@asynccontextmanager
async def lifespan(app: FastAPI):
    global sessions
    try:
        sessions = json.load(open(sessions_file_name))
    except json.decoder.JSONDecodeError:
        sessions = {}
    except FileNotFoundError:
        with open(sessions_file_name, 'x') as created:
            created.write(json.dumps(sessions))
    yield

    json.dump(sessions, open(sessions_file_name, 'w'))

app = FastAPI(title="Channel Parser", lifespan=lifespan)

async def create_client(username: str, password: str, session_name: str, phone_code_hash: str):
    sessions[username] = {'password': sha256(password.encode()).hexdigest(), 'session_name': session_name, 'phone_code_hash': phone_code_hash}


async def get_client(username: str, password: str) -> TelegramClient:
    client = sessions.get(username)
    if not client:
        raise HTTPException(status_code=404, detail="client not found")
    if sha256(password.encode()).hexdigest() != client.get('password'):
        raise HTTPException(status_code=401, detail="invalid password")
    return TelegramClient(client.get('session_name'), API_ID, API_HASH)


async def client_for_sign_in(username: str, password: str):
    client = await get_client(username, password)
    return client, sessions.get(username)['phone_code_hash']


async def delete_client(username: str, password: str) -> bool:
    client = sessions.pop(username, None)
    if not client:
        raise HTTPException(status_code=404, detail="client not found")
    if sha256(password.encode()).hexdigest() != client.get('password'):
        raise HTTPException(status_code=401, detail="invalid password")
    return True


@app.post('/parse_channel')
async def parse_channel(
        background_tasks: BackgroundTasks,
        src_channel: str,
        target_channel: str,
        limit: int | None = None,
        client: TelegramClient = Depends(get_client),
        ):
    background_tasks.add_task(copy_messages_from_channel, client, src_channel, target_channel, limit)
    return {'status': 'success', 'message': 'started copying messages'}


@app.post('/parse_channel_by_id')
async def parse_channel_by_id(
        background_tasks: BackgroundTasks,
        src_channel: str,
        target_channel: str,
        ids: list[int] = Body(),
        client: TelegramClient = Depends(get_client),
        ):
    background_tasks.add_task(copy_by_id, client, src_channel, target_channel, ids)
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
    await create_client(username, password, session_name, phone_code_hash)
    await client.disconnect()
    return {'status': 'success', 'message': 'authorization successful, send verification code to sign_in'}


@app.post('/account/sign_in')
async def sign_in(phone: str, verification_code: str, two_factor_auth_password: str | None = None, client: tuple[TelegramClient, str] = Depends(client_for_sign_in)):
    client, phone_code_hash = client
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=verification_code, phone_code_hash=phone_code_hash)
    except rpcerrorlist.SessionPasswordNeededError:
        try:
            await client.sign_in(password=two_factor_auth_password)
        except rpcerrorlist.SessionPasswordNeededError as err:
            raise HTTPException(status_code=404, detail=str(err))
    await client.disconnect()
    return {'status': 'success', 'message': 'sign in successful'}


@app.get('/account')
async def get_account(client: TelegramClient = Depends(get_client)):
    await client.connect()
    try:
        me = (await client.get_me()).__dict__
        return {'status': 'success', 'message': 'account successfully found', 'detail': {
            'id': me.get('id'),
            'username': me.get('username'),
            'first_name': me.get('first_name'),
            'last_name': me.get('last_name'),
            'phone': me.get('phone'),
        }}
    except rpcerrorlist.SessionPasswordNeededError:
        raise HTTPException(status_code=404, detail='account does not full authorized in this service')
    finally:
        await client.disconnect()


@app.post('/account/delete')
async def delete_account(username: str, password: str):
    await delete_client(username, password)
    try:
        os.remove(f'sessions/{username}.session')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='session not found')
    else:
        return {'status': 'success', 'message': 'account successfully deleted'}
