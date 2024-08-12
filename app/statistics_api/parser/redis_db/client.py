import redis

from . import config


def get_client():
    return redis.Redis(host="redis", port=config.REDIS_TEMPORARY_STORAGE_PORT, db=0)
