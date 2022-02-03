from dataclasses import dataclass
from starlette.requests import Request

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.facade import BTCWalletCore

wallet_api = APIRouter()


def get_btc_wallet_core(request: Request) -> BTCWalletCore:
    return request.app.state.core


@dataclass
class BaseApiInput:
    pass


class BaseApiOutput(BaseModel):
    result_code: int


class RegisterUserIn(BaseApiInput):
    name: str


class RegisterUserOut(BaseApiOutput):
    api_key: str


# TODO: actiavate response_model
# @wallet_api.post("/users", response_model=RegisterUserOut)
@wallet_api.post("/users")
def register_user(
    input_data: RegisterUserIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    result = core.add_user()
    return result


class CreateWalletIn(BaseApiInput):
    api_key: str


class CreateWalletOut(BaseApiOutput):
    address: str
    btc_balance: float
    usd_balance: float


@wallet_api.post("/wallets", response_model=CreateWalletOut)
def create_wallet(
    input_data: CreateWalletIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass


class FetchWalletOut(BaseApiOutput):
    address: str
    btc_balance: float
    usd_balance: float


@wallet_api.get("/wallets/{address}", response_model=FetchWalletOut)
def fetch_wallet(
    address: str, api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass


class CreateTransactionIn(BaseApiInput):
    api_key: str
    source_address: str
    dest_address: str
    amount_btc: float = Field(
        ..., gt=0, description="The amount must be greater than zero"
    )


class CreateTransactionOut(BaseApiOutput):
    pass


@wallet_api.post("/transactions", response_model=CreateTransactionOut)
def create_transaction(
    input_data: CreateTransactionIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass


class Transaction(BaseModel):
    todo: str


class FetchUserTransactionsOut(BaseApiOutput):
    transactions: list[Transaction]


@wallet_api.get("/transactions", response_model=FetchUserTransactionsOut)
def fetch_user_transactions(
    api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass


class FetchWalletTransactionsOut(BaseApiOutput):
    transactions: list[Transaction]


@wallet_api.get(
    "/wallets/{address}/transactions", response_model=FetchWalletTransactionsOut
)
def fetch_wallet_transactions(
    address: str, api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass


class FetchStatisticsOut(BaseApiOutput):
    num_transactions: int
    platform_profit: float


@wallet_api.get("/statistics", response_model=FetchStatisticsOut)
def fetch_statistics(
    admin_api_key: str, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    pass
