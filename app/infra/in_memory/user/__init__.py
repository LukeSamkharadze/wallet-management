import datetime
from dataclasses import dataclass

from sqlalchemy import Column, Date, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection


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
class UserInMemoryRepository:
    TABLE_NAME = "User"

    def get_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TABLE_NAME,
            metadata,
            Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("Api_key", String, nullable=False),
            Column("Name", String, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def create_table(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.TABLE_NAME):
            metadata = MetaData(engine)
            metadata.create_all(engine)

    def add_user(self, engine: MockConnection, user: UserInMemoryIn) -> UserInMemoryIn:
        metadata = MetaData(engine)
        users = self.get_table(metadata)
        ins = users.insert().values(
            Api_key=user.api_key,
            Name=user.name,
            create_date_utc=user.create_date_utc,
        )
        con = engine.connect()
        con.execute(ins)
        return user
