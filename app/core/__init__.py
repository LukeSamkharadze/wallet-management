import datetime
from dataclasses import dataclass
from typing import Protocol

from app.utils.result_codes import ResultCode


@dataclass
class BaseInteractorOutput:
    result_code: ResultCode


@dataclass
class BaseDbOutput:
    result_code: ResultCode


@dataclass
class DbAddUserIn:
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class DbAddUserOut(BaseDbOutput):
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
class DbAddTransactionOut(BaseDbOutput):
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class DbUserTransactionsOutput(BaseDbOutput):
    user_transactions: list[DbAddTransactionOut]


@dataclass
class DbWalletTransactionsOutput(BaseDbOutput):
    wallet_transactions: list[DbAddTransactionOut]


@dataclass
class DbAddWalletIn:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class DbAddWalletOut(BaseDbOutput):
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class DbUpdateCommissionStatsIn:
    commission_amount_btc: float
    create_date_utc: datetime.datetime


@dataclass
class DbUpdateCommissionStatsOut(BaseDbOutput):
    pass


@dataclass
class DbGetWalletIn:
    public_key: str


@dataclass
class DbGetWalletOut(BaseDbOutput):
    public_key: str = ""
    api_key: str = ""
    btc_amount: float = 0


@dataclass
class DbGetUserWalletCountIn:
    api_key: str


@dataclass
class DbGetUserWalletCountOut(BaseDbOutput):
    wallet_count: int


@dataclass
class DbUpdateWalletBalanceIn:
    public_key: str
    amount: float


@dataclass
class DbUpdateWalletBalanceOut(BaseDbOutput):
    pass


class IBTCWalletRepository(Protocol):
    def add_user(self, user: DbAddUserIn) -> DbAddUserOut:
        pass

    def add_wallet(self, wallet: DbAddWalletIn) -> DbAddWalletOut:
        pass

    def count_wallets_of_user(
        self, count_input: DbGetUserWalletCountIn
    ) -> DbGetUserWalletCountOut:
        pass

    def update_wallet_balance(
        self, update_input: DbUpdateWalletBalanceIn
    ) -> DbUpdateWalletBalanceOut:
        pass

    def add_transaction(self, transaction: DbAddTransactionIn) -> DbAddTransactionOut:
        pass

    def fetch_user_transactions(self, api_key: str) -> DbUserTransactionsOutput:
        pass

    def update_commission_stats(
        self, commission: DbUpdateCommissionStatsIn
    ) -> DbUpdateCommissionStatsOut:
        pass

    def fetch_wallet_transactions(
        self, address: str, api_key: str
    ) -> DbWalletTransactionsOutput:
        pass

    def get_wallet(self, wallet: DbGetWalletIn) -> DbGetWalletOut:
        pass
