from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv() # force load it

class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_port: str
    db_name: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore
