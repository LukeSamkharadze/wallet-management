from fastapi import FastAPI

from app.infra.api import wallet_api


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(wallet_api)
    return app
