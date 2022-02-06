from dataclasses import dataclass
import datetime

from starlette.requests import Request

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.facade import BTCWalletCore
from app.core.transaction.interactor import TransactionInput
from app.core.user.interactor import UserInput
from app.core.wallet.interactor import WalletInput

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


@dataclass()
class RegisterUserOut:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


# TODO: actiavate response_model
# @wallet_api.post("/users", response_model=RegisterUserOut)
@wallet_api.post("/users")
def register_user(
    input_data: RegisterUserIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> RegisterUserOut:
    result = core.add_user(UserInput(name=input_data.name))
    return str(
        RegisterUserOut(
            name=result.name,
            api_key=result.api_key,
            create_date_utc=result.create_date_utc,
        )
    )


class CreateWalletIn(BaseApiInput):
    api_key: str


@dataclass()
class CreateWalletOut:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


# TODO: actiavate response_model
# @wallet_api.post("/wallets", response_model=CreateWalletOut)
@wallet_api.post("/wallets")
def create_wallet(
    input_data: CreateWalletIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> CreateWalletOut:
    result = core.add_wallet(WalletInput(api_key=input_data.api_key))
    return str(
        CreateWalletOut(
            api_key=result.api_key,
            create_date_utc=result.create_date_utc,
            public_key=result.public_key,
            btc_amount=result.btc_amount,
        )
    )


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
    pass


class CreateTransactionIn(BaseApiInput):
    api_key: str
    source_address: str
    dest_address: str
    amount_btc: float = Field(
        ..., gt=0, description="The amount must be greater than zero"
    )


@dataclass()
class CreateTransactionOut:
    api_key: str
    source_address: str
    dest_address: str
    amount_btc: float
    commission: float
    create_date_utc: datetime.datetime


# TODO: actiavate response_model
# @wallet_api.post("/transactions", response_model=CreateTransactionOut)
@wallet_api.post("/transactions")
def create_transaction(
    input_data: CreateTransactionIn, core: BTCWalletCore = Depends(get_btc_wallet_core)
) -> None:
    result = core.add_transaction(
        TransactionInput(
            src_api_key=input_data.api_key,
            src_public_key=input_data.source_address,
            dst_public_key=input_data.dest_address,
            btc_amount=input_data.amount_btc,
        )
    )
    return str(
        CreateTransactionOut(
            api_key=result.src_api_key,
            source_address=result.src_public_key,
            dest_address=result.dst_public_key,
            amount_btc=result.btc_amount,
            commission=result.commission,
            create_date_utc=result.create_date_utc,
        )
    )


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
