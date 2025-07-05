import os

from fastapi import FastAPI

from app.core import IWalletRepository
from app.core.crypto_market_api.multi_currency_api import MultiCurrencyApi
from app.core.facade import WalletCore
from app.core.observers.transaction_observers import SystemTransactionObserver
from app.infra.api import wallet_api
from app.infra.data_repository import MultiCurrencyWalletRepository
from app.utils import get_root_path


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(wallet_api)
    app.state.core = WalletCore.create(
        wallet_repository=setup_wallet_repository(), crypto_market_api=MultiCurrencyApi()
    )
    app.state.core.attach(SystemTransactionObserver())
    return app


def setup_wallet_repository() -> IWalletRepository:
    root_dir = get_root_path()
    repository = MultiCurrencyWalletRepository(
        connection_string=f"sqlite:///{root_dir}{os.sep}identifier.sqlite"
    )
    return repository
