from fastapi import FastAPI

from app.infra.api import wallet_api
from app.core.facade import BTCWalletCore
from app.core.facade import IBTCWalletRepository
from app.infra.in_memory import BTCWalletInMemoryRepository


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(wallet_api)
    app.state.core = BTCWalletCore.create(setup_user_repository())
    return app


def setup_user_repository() -> IBTCWalletRepository:
    repository = BTCWalletInMemoryRepository(
        connection_string="sqlite:////Users/daviti_kokaia/Desktop/des/Design-Patterns-Final-Project/identifier.sqlite"
    )
    return repository
