# backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEV_JWT_SECRET = "placeholder_secret_for_development_only"


class Settings(BaseSettings):
    # Websupport Standard API key (pre DNS záznamy, FTP účty)
    WEBSUPPORT_API_KEY: str = ""
    WEBSUPPORT_SECRET: str = ""
    # Websupport DynDNS API key
    WEBSUPPORT_DYNDNS_KEY: str = ""
    WEBSUPPORT_DYNDNS_SECRET: str = ""

    # Forpsi domains (manual list, comma-separated) — Forpsi has no REST API
    FORPSI_DOMAINS: str = ""

    DATABASE_URL: str = "sqlite:///./test.db"
    CERTBOT_EMAIL: str = ""
    ENV: str = "development"
    # In production, this MUST be set via environment variable
    JWT_SECRET: str = DEFAULT_DEV_JWT_SECRET
    JWT_EXPIRE_MINUTES: int = 1440

    # WebSocket token (optional service-to-service auth bypass)
    WS_TOKEN: str = ""

    # Per-domain polling intervals (JSON string, e.g. '{"critical.com": 30, "default": 60}')
    DOMAIN_POLL_INTERVALS: str = ""

    # VPS provisioning — cloud provider API tokens
    HETZNER_API_TOKEN: str = ""
    DIGITALOCEAN_API_TOKEN: str = ""
    
    # OpenAI (GPT-4) for DNS Autopilot
    OPENAI_API_KEY: str = ""

    # VPS Credentials for general management
    VPS_HOST: str = ""
    VPS_USER: str = ""
    VPS_PASS: str = ""

    # Defaults for local development
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,0.0.0.0,localhost:8000,localhost:3000,testserver"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def validate_security_settings(self) -> None:
        env = self.ENV.lower()
        if env != "production":
            return

        if self.JWT_SECRET == DEFAULT_DEV_JWT_SECRET:
            raise RuntimeError("JWT_SECRET must be explicitly configured in production.")

        if len(self.JWT_SECRET) < 32:
            raise RuntimeError("JWT_SECRET must be at least 32 characters in production.")

settings = Settings()
