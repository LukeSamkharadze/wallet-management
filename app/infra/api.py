import datetime
from dataclasses import dataclass

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.requests import Request

from app.core.facade import BTCWalletCore
from app.core.transaction.transaction_interactor import (
    TransactionInput,
    TransactionOutput,
    UserTransactionsOutput,
)
from app.core.user.user_interactor import UserInput, UserOutput
from app.core.wallet.wallet_interactor import (
    WalletInput,
    WalletOutput,
    WalletTransactionsOutput,
)

wallet_api = APIRouter()


def get_btc_wallet_core(request: Request) -> BTCWalletCore:
    # https://github.com/encode/starlette/issues/545
    # Nothing we can do about the type error here...
    return request.app.state.core  # type: ignore


@dataclass
class BaseApiInput:
    pass


class BaseApiOutput(BaseModel):
    result_code: int


class RegisterUserIn(BaseApiInput):
    name: str


class RegisterUserOut(BaseApiOutput):
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@wallet_api.post("/users", response_model=RegisterUserOut)
def register_user(
    input_data: RegisterUserIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> UserOutput:
    result = core.add_user(UserInput(name=input_data.name))
    return result


class CreateWalletIn(BaseApiInput):
    api_key: str


class CreateWalletOut(BaseApiOutput):
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@wallet_api.post("/wallets", response_model=CreateWalletOut)
def create_wallet(
    input_data: CreateWalletIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> WalletOutput:
    result = core.add_wallet(WalletInput(api_key=input_data.api_key))
    return result


class FetchWalletIn(BaseApiInput):
    address: str
    btc_balance: float
    usd_balance: float


class FetchWalletOut(BaseApiOutput):
    address: str
    btc_balance: float
    usd_balance: float


@wallet_api.get("/wallets/{address}", response_model=FetchWalletOut)
def fetch_wallet(
    address: str, api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    return core.fetch_wallet()


class CreateTransactionIn(BaseApiInput):
    api_key: str
    source_address: str
    dest_address: str
    btc_amount: float = Field(
        ..., gt=0, description="The amount must be greater than zero"
    )


class CreateTransactionOut(BaseApiOutput):
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    dest_btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@wallet_api.post("/transactions", response_model=CreateTransactionOut)
def create_transaction(
    input_data: CreateTransactionIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> TransactionOutput:
    result = core.add_transaction(
        TransactionInput(
            src_api_key=input_data.api_key,
            src_public_key=input_data.source_address,
            dst_public_key=input_data.dest_address,
            btc_amount=input_data.btc_amount,
        )
    )
    return result


class Transaction(BaseModel):
    todo: str


class UserTransactionOut(BaseModel):
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.date


class FetchUserTransactionsOut(BaseApiOutput):
    user_transactions: list[UserTransactionOut]


@wallet_api.get("/transactions", response_model=FetchUserTransactionsOut)
def fetch_user_transactions(
    api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> UserTransactionsOutput:
    return core.fetch_user_transactions(api_key)


class FetchWalletTransactionsOut(BaseApiOutput):
    wallet_transactions: list[UserTransactionOut]


@wallet_api.get(
    "/wallets/{address}/transactions", response_model=FetchWalletTransactionsOut
)
def fetch_wallet_transactions(
    address: str, api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> WalletTransactionsOutput:
    return core.fetch_wallet_transactions(address, api_key)


class FetchStatisticsOut(BaseApiOutput):
    num_transactions: int
    platform_profit: float


@wallet_api.get("/statistics", response_model=FetchStatisticsOut)
def fetch_statistics(
    admin_api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass
