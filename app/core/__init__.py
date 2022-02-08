import datetime
from dataclasses import dataclass
from typing import Protocol


@dataclass
class UserInMemoryIn:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class UserInMemoryOut:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class TransactionInMemoryIn:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class TransactionInMemoryOut:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class WalletInMemoryIn:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class WalletInMemoryOut:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


class IBTCWalletRepository(Protocol):
    def add_user(self, user: UserInMemoryIn) -> UserInMemoryIn:
        pass

    def add_wallet(self, wallet: WalletInMemoryIn) -> WalletInMemoryIn:
        pass

    def add_transaction(
        self, transaction: TransactionInMemoryIn
    ) -> TransactionInMemoryIn:
        pass
