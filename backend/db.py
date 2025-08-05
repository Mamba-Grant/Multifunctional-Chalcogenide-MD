from functools import lru_cache
from typing import Any
from psycopg_pool import AsyncConnectionPool
from config import Settings, get_settings

settings: Settings = get_settings()

conninfo = f"user={settings.db_user} password={settings.db_password} host={settings.db_host} port={settings.db_port} dbname={settings.db_name}"

@lru_cache()
def get_async_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(conninfo=conninfo)
