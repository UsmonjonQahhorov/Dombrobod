import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER = 'postgres'
    DB_PASSWORD = '1'  # Ensure this is a string
    DB_NAME = 'dombrobod_db'
    DB_PORT = '5432'  # Ensure this is a string
    DB_HOST = 'postgres'  # Specify the database host
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
