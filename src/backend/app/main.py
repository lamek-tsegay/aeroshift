from fastapi import FastAPI

from app.api.v1 import health, states
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Aero API", version="0.1.0")
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(states.router, prefix="/api/v1")
    return app


app = create_app()
