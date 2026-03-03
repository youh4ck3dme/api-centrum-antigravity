# backend/app/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    WEBSUPPORT_API_KEY: str = ""
    WEBSUPPORT_SECRET: str = ""
    DATABASE_URL: str = "sqlite:///./test.db"
    CERTBOT_EMAIL: str = ""
    ENV: str = "development"
    JWT_SECRET: str = "veľmi_dlhý_secret_kľúč_minimálne_32_znakov_pre_bezpečnosť"
    JWT_EXPIRE_MINUTES: int = 1440
    
    # Produkčné nastavenia
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,0.0.0.0,localhost:5555,localhost:5556"
    CORS_ORIGINS: str = "http://localhost:5555,http://localhost:5556,http://127.0.0.1:5555,http://127.0.0.1:5556"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

