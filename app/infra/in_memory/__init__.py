import sqlite3
from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection

from app.core import IBTCWalletRepository
from app.infra.in_memory.transaction import (
    TransactionInMemoryIn,
    TransactionInMemoryRepository,
)
from app.infra.in_memory.user import UserInMemoryIn, UserInMemoryRepository
from app.infra.in_memory.wallet import WalletInMemoryIn, WalletInMemoryRepository


@dataclass
class BTCWalletInMemoryRepository(IBTCWalletRepository):

    connection: sqlite3.Connection
    userInMemoryRepository: UserInMemoryRepository
    walletInMemoryRepository: WalletInMemoryRepository
    transactionInMemoryRepository: TransactionInMemoryRepository
    engine: MockConnection

    # TODO prepare database creation
    def __init__(self, connection_string: str) -> None:
        self.__create_connection(connection_string)
        self.userInMemoryRepository = UserInMemoryRepository()
        self.userInMemoryRepository.create_table(self.engine)
        self.walletInMemoryRepository = WalletInMemoryRepository()
        self.walletInMemoryRepository.create_table(self.engine)
        self.transactionInMemoryRepository = TransactionInMemoryRepository()
        self.transactionInMemoryRepository.create_table(self.engine)

    def __create_connection(self, connection_string: str) -> None:
        self.engine = create_engine(connection_string, echo=True)

    def add_user(self, user_input: UserInMemoryIn) -> UserInMemoryIn:
        return self.userInMemoryRepository.add_user(self.engine, user_input)

    def add_wallet(self, wallet_input: WalletInMemoryIn) -> WalletInMemoryIn:
        return self.walletInMemoryRepository.add_wallet(self.engine, wallet_input)

    def add_transaction(
        self, transaction_input: TransactionInMemoryIn
    ) -> TransactionInMemoryIn:
        return self.transactionInMemoryRepository.add_transaction(
            self.engine, transaction_input
        )
