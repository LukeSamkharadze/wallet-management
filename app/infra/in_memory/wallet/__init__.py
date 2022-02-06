import datetime

from pydantic.dataclasses import dataclass

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Float
from sqlalchemy.engine.mock import MockConnection


@dataclass()
class WalletInMemoryIn:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass()
class WalletInMemoryOut:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class WalletInMemoryRepository:
    Variable_tableName = "Wallet"
    # TODO add foreign key logic
    def getTable(self, metadata: MetaData):
        return Table(
            self.Variable_tableName,
            metadata,
            Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("public_key", String, nullable=False),
            Column("btc_amount", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
            Column("Api_key", String, nullable=False),
        )

    def create_table(self, engine: MockConnection):
        if not engine.dialect.has_table(engine.connect(), self.Variable_tableName):
            metadata = MetaData(engine)
            self.getTable(metadata)
            metadata.create_all(engine)

    def add_wallet(self, engine: MockConnection, wallet: WalletInMemoryIn):
        metadata = MetaData(engine)
        tbl = self.getTable(metadata)
        tbl.insert().values
        ins = tbl.insert().values(
            Api_key=wallet.api_key,
            create_date_utc=wallet.create_date_utc,
            public_key=wallet.public_key,
            btc_amount=wallet.btc_amount,
        )
        con = engine.connect()
        con.execute(ins)
        return wallet
