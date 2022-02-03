import sqlite3
from dataclasses import dataclass

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date

from app.core.facade import IBTCWalletRepository
from app.infra.in_memory.user import UserInMemoryRepository


@dataclass
class BTCWalletInMemoryRepository:
    connection: sqlite3.Connection
    userInMemoryRepository: UserInMemoryRepository
    engine: MockConnection

    # TODO prepare database creation
    def __init__(self, connection_string: str) -> None:
        self.__create_connection(connection_string)
        self.userInMemoryRepository = UserInMemoryRepository()
        self.__create_database_schema()

    def __create_connection(self, connection_string: str) -> None:
        # self.engine = create_engine(connection_string, echo=True)
        pass

    def __create_database_schema(self) -> None:
        pass

    def __create_table(self) -> None:
        Variable_tableName = "User"
        if not self.engine.dialect.has_table(
            self.engine, Variable_tableName
        ):  # If table don't exist, Create.
            metadata = MetaData(self.engine)
            # Create a table with the appropriate Columns
            Table(
                Variable_tableName,
                metadata,
                Column("Id", Integer, primary_key=True, nullable=False),
                Column("Api_key", String, nullable=False),
                Column("Name", String, nullable=False),
                Column("create_date_utc", Date, nullable=False),
            )
            metadata.create_all(self.engine)

    def add_user(self):
        return self.userInMemoryRepository.add_user()
