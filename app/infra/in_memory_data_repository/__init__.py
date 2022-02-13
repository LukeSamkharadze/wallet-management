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
        self.truncate()

    def truncate(self) -> None:
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
        for i, wallet in enumerate(self.wallets_table):
            if wallet.public_key == update_input.public_key:
                wallet.btc_amount += update_input.amount
                self.wallets_table[i].btc_amount += update_input.amount
                return DbUpdateWalletBalanceOut(result_code=ResultCode.SUCCESS)
        return DbUpdateWalletBalanceOut(result_code=ResultCode.WALLET_NOT_ACCESSIBLE)

    def add_transaction(self, transaction: DbAddTransactionIn) -> DbAddTransactionOut:
        self.transactions_table.append(
            InMemoryTransactionEntry(
                id=len(self.transactions_table),
                src_api_key=transaction.src_api_key,
                src_public_key=transaction.dst_public_key,
                dst_public_key=transaction.dst_public_key,
                btc_amount=transaction.btc_amount,
                commission=transaction.commission,
                create_date_utc=transaction.create_date_utc,
            )
        )
        return DbAddTransactionOut(
            result_code=ResultCode.SUCCESS,
            src_api_key=transaction.src_api_key,
            src_public_key=transaction.src_public_key,
            dst_public_key=transaction.dst_public_key,
            btc_amount=transaction.btc_amount,
            commission=transaction.commission,
            create_date_utc=transaction.create_date_utc,
        )

    def fetch_user_transactions(self, api_key: str) -> DbUserTransactionsOutput:
        transactionList: list[DbAddTransactionOut] = []
        for transaction in self.transactions_table:
            if transaction.src_api_key == api_key:
                transactionList.append(
                    DbAddTransactionOut(
                        result_code=ResultCode.SUCCESS,
                        src_api_key=transaction.src_api_key,
                        src_public_key=transaction.src_public_key,
                        dst_public_key=transaction.dst_public_key,
                        btc_amount=transaction.btc_amount,
                        commission=transaction.commission,
                        create_date_utc=transaction.create_date_utc,
                    )
                )
        return DbUserTransactionsOutput(
            result_code=ResultCode.SUCCESS, user_transactions=transactionList
        )

    def update_commission_stats(
        self, commission: DbUpdateCommissionStatsIn
    ) -> DbUpdateCommissionStatsOut:
        if len(self.transaction_stats_table) == 0:
            self.transaction_stats_table.append(
                InMemoryTransactionStatEntry(
                    id=len(self.transaction_stats_table),
                    commission_sum_btc=commission.commission_amount_btc,
                    total_transactions=1,
                    stat_date_utc=commission.create_date_utc,
                )
            )
        else:
            self.transaction_stats_table[
                0
            ].commission_sum_btc += commission.commission_amount_btc
            self.transaction_stats_table[0].total_transactions += 1
        return DbUpdateCommissionStatsOut(result_code=ResultCode.SUCCESS)

    def fetch_wallet_transactions(
        self, address: str, api_key: str
    ) -> DbWalletTransactionsOutput:
        transactionList: list[DbAddTransactionOut] = []
        for transaction in self.transactions_table:
            if (
                transaction.src_api_key == api_key
                and transaction.src_public_key == address
            ):
                transactionList.append(
                    DbAddTransactionOut(
                        result_code=ResultCode.SUCCESS,
                        src_api_key=transaction.src_api_key,
                        src_public_key=transaction.src_public_key,
                        dst_public_key=transaction.dst_public_key,
                        btc_amount=transaction.btc_amount,
                        commission=transaction.commission,
                        create_date_utc=transaction.create_date_utc,
                    )
                )
        return DbWalletTransactionsOutput(
            result_code=ResultCode.SUCCESS, wallet_transactions=transactionList
        )

    def fetch_wallet(self, wallet: DbGetWalletIn) -> DbGetWalletOut:
        for wallets in self.wallets_table:
            if wallet.public_key == wallets.public_key:
                return DbGetWalletOut(
                    result_code=ResultCode.SUCCESS,
                    public_key=wallets.public_key,
                    api_key=wallets.api_key,
                    btc_amount=wallets.btc_amount,
                )
        return DbGetWalletOut(
            result_code=ResultCode.WALLET_NOT_ACCESSIBLE,
            public_key="",
            api_key="",
            btc_amount=0,
        )

    def fetch_statistics(
        self, stats_input: DbFetchStatisticsIn
    ) -> DbFetchStatisticsOut:
        if len(self.transaction_stats_table) == 0:
            return DbFetchStatisticsOut(
                result_code=ResultCode.SUCCESS,
                commissions_sum_btc=0,
                transactions_total_amount=0,
            )
        else:
            return DbFetchStatisticsOut(
                result_code=ResultCode.SUCCESS,
                commissions_sum_btc=self.transaction_stats_table[0].commission_sum_btc,
                transactions_total_amount=self.transaction_stats_table[
                    0
                ].total_transactions,
            )
