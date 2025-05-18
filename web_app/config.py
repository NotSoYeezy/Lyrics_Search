import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG=os.environ.get("DEBUG", "False").lower() == 'true'
    DATABASE_URL = os.environ.get("DATABASE_URL")