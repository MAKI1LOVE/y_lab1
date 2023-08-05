import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_PORT = os.getenv('DB_PORT')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')

        self.DB_URL = \
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

        self.REDIS_NAME = os.getenv('REDIS_NAME')
        self.REDIS_HOST = os.getenv('REDIS_HOST')
        self.REDIS_PORT = os.getenv('REDIS_PORT')
        self.REDIS_USER = os.getenv('REDIS_USER')
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

        self.REDIS_URL = \
            f'redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_NAME}'


settings = Settings()
