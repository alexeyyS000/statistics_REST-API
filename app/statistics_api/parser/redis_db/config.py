import os

from dotenv import load_dotenv

load_dotenv()


REDIS_TEMPORARY_STORAGE_HOST = os.environ.get("REDIS_TEMPORARY_STORAGE_HOST")
REDIS_TEMPORARY_STORAGE_PORT = os.environ.get("REDIS_TEMPORARY_STORAGE_PORT")
REDIS_TEMPORARY_STORAGE_DB = os.environ.get("REDIS_TEMPORARY_STORAGE_PORT")
