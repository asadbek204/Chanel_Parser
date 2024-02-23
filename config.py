from os import environ
from dotenv import load_dotenv

load_dotenv('.env')

API_ID = environ.get('API_ID')
API_HASH = environ.get("API_HASH")
LOGS_PATH = environ.get("LOGS_PATH")
SECRET_KEY = environ.get("SECRET_KEY")
COOKIE_NAME = environ.get("COOKIE_NAME")
COOKIE_MAX_AGE = environ.get("COOKIE_MAX_AGE")
AUTH_BACKEND_NAME = environ.get("AUTH_BACKEND_NAME")
LIFE_TIME_SECONDS = environ.get("LIFE_TIME_SECONDS")
