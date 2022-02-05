import datetime

from pydantic.dataclasses import dataclass

from sqlalchemy import  MetaData, Table, Column, Integer, String, Date
from sqlalchemy.engine.mock import MockConnection



@dataclass()
class UserInMemoryIn:
    name: str
    api_key: str
    create_date_utc: datetime.datetime

@dataclass()
class UserInMemoryOut:
    name: str
    api_key: str
    create_date_utc: datetime.datetime

@dataclass
class UserInMemoryRepository:
    Variable_tableName = "User"

    def getTable(self, metadata: MetaData):
        return Table(
                self.Variable_tableName,
                metadata,
                Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
                Column("Api_key", String, nullable=False),
                Column("Name", String, nullable=False),
                Column("create_date_utc", Date, nullable=False),
            )

    def create_table(self, engine: MockConnection):
        if not engine.dialect.has_table(engine.connect(),
                                             self.Variable_tableName):
            metadata = MetaData(engine)
            tbl = self.getTable(metadata)
            metadata.create_all(engine)

    def add_user(self, engine: MockConnection, user: UserInMemoryIn):
        metadata = MetaData(engine)
        users = self.getTable(metadata)
        users.insert().values
        ins = users.insert().values(
            Api_key = user.api_key,
            Name=user.name,
            create_date_utc=user.create_date_utc,
        )
        con = engine.connect()
        con.execute(ins)
        return user

