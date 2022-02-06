import datetime

from pydantic.dataclasses import dataclass

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Float
from sqlalchemy.engine.mock import MockConnection


@dataclass()
class TransactionInMemoryIn:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass()
class TransactionInMemoryOut:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class TransactionInMemoryRepository:
    Variable_tableName = "transaction"
    # TODO add foreign key logic
    def getTable(self, metadata: MetaData):
        return Table(
            self.Variable_tableName,
            metadata,
            Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("src_api_key", String, nullable=False),
            Column("src_public_key", String, nullable=False),
            Column("dst_public_key", String, nullable=False),
            Column("btc_amount", Float, nullable=False),
            Column("commission", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def create_table(self, engine: MockConnection):
        if not engine.dialect.has_table(engine.connect(), self.Variable_tableName):
            metadata = MetaData(engine)
            self.getTable(metadata)
            metadata.create_all(engine)

    def add_transaction(
        self, engine: MockConnection, transaction: TransactionInMemoryIn
    ):
        metadata = MetaData(engine)
        tbl = self.getTable(metadata)
        tbl.insert().values
        ins = tbl.insert().values(
            src_api_key=transaction.src_api_key,
            src_public_key=transaction.src_public_key,
            dst_public_key=transaction.dst_public_key,
            btc_amount=transaction.btc_amount,
            commission=transaction.commission,
            create_date_utc=transaction.create_date_utc,
        )
        con = engine.connect()
        con.execute(ins)
        return transaction
