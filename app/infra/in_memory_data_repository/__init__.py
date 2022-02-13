from dataclasses import dataclass
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
from app.utils.result_codes import ResultCode


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


@dataclass
class InMemoryBtcWalletRepository(IBTCWalletRepository):
    users_table: list[InMemoryUserEntry]
    transactions_table: list[InMemoryTransactionEntry]
    transaction_stats_table: list[InMemoryTransactionStatEntry]
    wallets_table: list[InMemoryWalletEntry]

    def __init__(self) -> None:
        self.users_table = []
        self.transactions_table = []
        self.transaction_stats_table = []
        self.wallets_table = []

    def add_user(self, user: DbAddUserIn) -> DbAddUserOut:
        self.users_table.append(
            InMemoryUserEntry(
                id=len(self.users_table),
                api_key=user.api_key,
                name=user.name,
                create_date_utc=user.create_date_utc,
            )
        )

        return DbAddUserOut(
            api_key=user.api_key,
            create_date_utc=user.create_date_utc,
            name=user.name,
            result_code=ResultCode.SUCCESS,
        )

    def add_wallet(self, wallet: DbAddWalletIn) -> DbAddWalletOut:
        self.wallets_table.append(
            InMemoryWalletEntry(
                id=len(self.wallets_table),
                public_key=wallet.public_key,
                btc_amount=wallet.btc_amount,
                create_date_utc=wallet.create_date_utc,
                api_key=wallet.api_key,
            )
        )
        return DbAddWalletOut(
            create_date_utc=wallet.create_date_utc,
            api_key=wallet.api_key,
            public_key=wallet.public_key,
            btc_amount=wallet.btc_amount,
            result_code=ResultCode.SUCCESS,
        )

    def count_wallets_of_user(
        self, count_input: DbGetUserWalletCountIn
    ) -> DbGetUserWalletCountOut:
        wallet_count = sum(
            wallet.api_key == count_input.api_key for wallet in self.wallets_table
        )
        return DbGetUserWalletCountOut(
            result_code=ResultCode.SUCCESS, wallet_count=wallet_count
        )

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
