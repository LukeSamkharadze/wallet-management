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
class DbUserTransactionsOutput:
    user_transactions: list[DbAddTransactionOut]


@dataclass
class DbWalletTransactionsOutput:
    wallet_transactions: list[DbAddTransactionOut]


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


@dataclass
class DbUpdateCommissionStatsIn:
    commission_amount_btc: float


class IBTCWalletRepository(Protocol):
    def add_user(self, user: DbAddUserIn) -> DbAddUserIn:
        pass

    def add_wallet(self, wallet: DbAddWalletIn) -> DbAddWalletIn:
        pass

    def count_wallets_of_user(self, api_key: str) -> int:
        pass

    def update_wallet_balance(self, public_key: str, amount: float) -> int:
        pass

    def add_transaction(self, transaction: DbAddTransactionIn) -> DbAddTransactionOut:
        pass

    def fetch_user_transactions(self, api_key: str) -> DbUserTransactionsOutput:
        pass

    def update_commission_stats(self, commission: DbUpdateCommissionStatsIn) -> int:
        pass

    def fetch_wallet_transactions(self, address: str, api_key: str) -> DbWalletTransactionsOutput:
        pass
