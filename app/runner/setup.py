import os

from fastapi import FastAPI

from app.core import IBTCWalletRepository
from app.core.crypto_market_api.blockchain_api import BlockchainApi
from app.core.facade import BTCWalletCore
from app.core.observers.transaction_observers import SystemTransactionObserver
from app.infra.api import wallet_api
from app.infra.data_repository import BTCWalletRepository
from app.utils import get_root_path


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(wallet_api)
    app.state.core = BTCWalletCore.create(
        btc_wallet_repository=setup_user_repository(), crypto_market_api=BlockchainApi()
    )
    app.state.core.attach(SystemTransactionObserver())
    return app


def setup_user_repository() -> IBTCWalletRepository:
    root_dir = get_root_path()
    repository = BTCWalletRepository(
        connection_string=f"sqlite:///{root_dir}{os.sep}database{os.sep}identifier.sqlite"
    )
    return repository
