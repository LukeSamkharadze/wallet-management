import datetime
from dataclasses import dataclass
from typing import Protocol


@dataclass
class DbAddUserIn:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class DbAddUserOut:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class DbAddTransactionIn:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class DbAddTransactionOut:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class DbAddWalletIn:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class DbAddWalletOut:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


class IBTCWalletRepository(Protocol):
    def add_user(self, user: DbAddUserIn) -> DbAddUserIn:
        pass

    def add_wallet(self, wallet: DbAddWalletIn) -> DbAddWalletIn:
        pass

    def add_transaction(self, transaction: DbAddTransactionIn) -> DbAddTransactionIn:
        pass
