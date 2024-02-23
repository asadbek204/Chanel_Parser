from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str
    phone_number: str


class UserCreate(schemas.BaseUserCreate):
    username: str
    phone_number: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    phone_number: str
