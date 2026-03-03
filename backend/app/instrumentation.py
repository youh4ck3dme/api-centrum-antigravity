# backend/app/instrumentation.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings

# Inicializácia Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN if hasattr(settings, "SENTRY_DSN") else None,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=settings.ENV
)

# Inicializácia Limiter (Rate Limiting)
limiter = Limiter(key_func=get_remote_address)
