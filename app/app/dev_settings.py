import os

import dotenv

from .settings import *

dotenv_path = os.path.join(os.path.dirname(__file__), ".env.local")

dotenv.load_dotenv(dotenv_path, override=True)

MINIO_STORAGE_ENDPOINT = os.environ.get("MINIO_STORAGE_ENDPOINT")

DATABASES["default"]["HOST"] = os.environ.get("DB_HOST")

CACHES["default"]["LOCATION"] = os.environ.get("CACHES")


CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

DEBUG = True

REDIS_TEMPORARY_STORAGE_HOST = os.environ.get("REDIS_TEMPORARY_STORAGE_HOST")
