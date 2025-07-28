from fastapi import FastAPI
from app.api import endpoints
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(endpoints.router)
