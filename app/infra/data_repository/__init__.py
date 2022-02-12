import sqlite3
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection

from app.core import (
    DbAddTransactionIn,
    DbAddTransactionOut,
    DbAddUserIn,
    DbAddUserOut,
    DbAddWalletIn,
    DbAddWalletOut,
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
from app.infra.data_repository.transaction.transaction_repository import (
    TransactionRepository,
)
from app.infra.data_repository.user.user_repository import UserRepository
from app.infra.data_repository.wallet.wallet_repository import WalletRepository


@dataclass
class BTCWalletRepository(IBTCWalletRepository):
    connection: sqlite3.Connection
    user_repository: UserRepository
    wallet_repository: WalletRepository
    transaction_repository: TransactionRepository
    engine: MockConnection

    # TODO prepare database creation
    def __init__(self, connection_string: str) -> None:
        self.__create_connection(connection_string)
        self.user_repository = UserRepository()
        self.user_repository.create_tables(self.engine)
        self.wallet_repository = WalletRepository()
        self.wallet_repository.create_tables(self.engine)
        self.transaction_repository = TransactionRepository()
        self.transaction_repository.create_tables(self.engine)

    def __create_connection(self, connection_string: str) -> None:
        self.engine = create_engine(connection_string, echo=True)

    def add_user(self, user_input: DbAddUserIn) -> DbAddUserOut:
        return self.user_repository.add_user(self.engine, user_input)

    def add_wallet(self, wallet_input: DbAddWalletIn) -> DbAddWalletOut:
        return self.wallet_repository.add_wallet(self.engine, wallet_input)

    def count_wallets_of_user(
        self, count_input: DbGetUserWalletCountIn
    ) -> DbGetUserWalletCountOut:
        return self.wallet_repository.count_wallets_of_user(self.engine, count_input)

    def update_wallet_balance(
        self, update_input: DbUpdateWalletBalanceIn
    ) -> DbUpdateWalletBalanceOut:
        return self.wallet_repository.update_wallet_balance(self.engine, update_input)

    def add_transaction(
        self, transaction_input: DbAddTransactionIn
    ) -> DbAddTransactionOut:
        return self.transaction_repository.add_transaction(
            self.engine, transaction_input
        )

    def fetch_user_transactions(self, api_key: str) -> DbUserTransactionsOutput:
        return self.transaction_repository.fetch_user_transactions(self.engine, api_key)

    def update_commission_stats(
        self, commission: DbUpdateCommissionStatsIn
    ) -> DbUpdateCommissionStatsOut:
        return self.transaction_repository.update_commission_stats(
            self.engine, commission
        )

    def fetch_wallet_transactions(
        self, address: str, api_key: str
    ) -> DbWalletTransactionsOutput:
        return self.transaction_repository.fetch_wallet_transactions(
            self.engine, address, api_key
        )

    def get_wallet(self, wallet: DbGetWalletIn) -> DbGetWalletOut:
        return self.wallet_repository.get_wallet(self.engine, wallet)
