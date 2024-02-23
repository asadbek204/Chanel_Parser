from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username: str = Column(String, unique=True, nullable=False)
    phone_number: str = Column(String, unique=True, nullable=False)
    phone_code_hash: str = Column(String, unique=True)
    session_name: str = Column(String, unique=True)


class MessageTransaction(Base):
    __tablename__ = "transactions"
    id: int = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user: int = Column(Integer, ForeignKey("users.id", ondelete='cascade'), nullable=False)
    source_channel: str = Column(String, nullable=False)
    target_channel: str = Column(String, nullable=False)


async_engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

