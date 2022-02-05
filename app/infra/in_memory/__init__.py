import sqlite3
from dataclasses import dataclass

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy import create_engine

from app.infra.in_memory.user import UserInMemoryRepository, UserInMemoryIn


@dataclass
class BTCWalletInMemoryRepository:
    connection: sqlite3.Connection
    userInMemoryRepository: UserInMemoryRepository
    engine: MockConnection

    # TODO prepare database creation
    def __init__(self, connection_string: str) -> None:
        self.__create_connection(connection_string)
        self.userInMemoryRepository = UserInMemoryRepository()
        self.userInMemoryRepository.create_table(self.engine)

    def __create_connection(self, connection_string: str) -> None:
        self.engine = create_engine(connection_string, echo=True)

    def add_user(self, user: UserInMemoryIn):
        return self.userInMemoryRepository.add_user(self.engine,user)
