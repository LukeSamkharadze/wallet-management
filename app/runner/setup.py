import os

from fastapi import FastAPI

from app.core import IBTCWalletRepository
from app.core.facade import BTCWalletCore
from app.infra.api import wallet_api
from app.infra.data_repository import BTCWalletRepository


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(wallet_api)
    app.state.core = BTCWalletCore.create(setup_user_repository())
    return app


def setup_user_repository() -> IBTCWalletRepository:
    root_dir = os.path.dirname(os.path.abspath("root_file.py"))
    repository = BTCWalletRepository(
        connection_string="sqlite:///" + root_dir + "\\app\\database\\identifier.sqlite"
    )
    return repository
