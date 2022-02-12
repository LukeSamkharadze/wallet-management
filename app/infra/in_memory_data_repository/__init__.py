from dataclasses import dataclass, field
from datetime import datetime

from app.core import (
    DbAddTransactionIn,
    DbAddTransactionOut,
    DbAddUserIn,
    DbAddUserOut,
    DbAddWalletIn,
    DbAddWalletOut,
    DbFetchStatisticsIn,
    DbFetchStatisticsOut,
    DbGetUserWalletCountIn,
    DbGetUserWalletCountOut,
    DbGetWalletIn,
    DbGetWalletOut,
    DbUpdateCommissionStatsIn,
    DbUpdateCommissionStatsOut,
    DbUpdateWalletBalanceIn,
    DbUpdateWalletBalanceOut,
    DbUserTransactionsOutput,
    DbWalletTransactionsOutput,
    IBTCWalletRepository,
)


@dataclass
class InMemoryTransactionEntry:
    id: int
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime


@dataclass
class InMemoryTransactionStatEntry:
    id: int
    commission_sum_btc: float
    total_transactions: int
    stat_date_utc: datetime


@dataclass
class InMemoryUserEntry:
    id: int
    api_key: str
    name: str
    create_date_utc: datetime


@dataclass
class InMemoryWalletEntry:
    id: int
    public_key: str
    btc_amount: float
    create_date_utc: datetime
    api_key: str


class InMemoryBtcWalletRepository(IBTCWalletRepository):
    users_table: list[InMemoryUserEntry] = field(default_factory=list)
    transactions_table: list[InMemoryUserEntry] = field(default_factory=list)
    transaction_stats_table: list[InMemoryUserEntry] = field(default_factory=list)
    wallets_table: list[InMemoryUserEntry] = field(default_factory=list)

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

    def fetch_wallet(self, wallet: DbGetWalletIn) -> DbGetWalletOut:
        pass

    def fetch_statistics(
        self, stats_input: DbFetchStatisticsIn
    ) -> DbFetchStatisticsOut:
        pass
