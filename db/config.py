import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_USER = 'postgres'
    DB_PASSWORD = 1
    DB_NAME = 'dombrobod_db'
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
