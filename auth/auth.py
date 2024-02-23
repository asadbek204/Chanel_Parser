from fastapi_users.authentication import CookieTransport, AuthenticationBackend, JWTStrategy
from config import SECRET_KEY, COOKIE_NAME, AUTH_BACKEND_NAME, COOKIE_MAX_AGE

cookie_transport = CookieTransport(cookie_name=COOKIE_NAME, cookie_max_age=COOKIE_MAX_AGE)
auth_backend = AuthenticationBackend(
    name=AUTH_BACKEND_NAME,
    transport=cookie_transport,
    get_strategy=lambda: JWTStrategy(secret=SECRET_KEY, lifetime_seconds=360)
)
