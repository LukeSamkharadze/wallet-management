from dataclasses import dataclass

from sqlalchemy import Column, Date, Float, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection

from app.core import DbAddTransactionIn, DbUserTransactionsOutput


@dataclass
class TransactionRepository:
    TABLE_NAME: str = "transaction"

    # TODO add foreign key logic
    def get_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TABLE_NAME,
            metadata,
            Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("src_api_key", String, nullable=False),
            Column("src_public_key", String, nullable=False),
            Column("dst_public_key", String, nullable=False),
            Column("btc_amount", Float, nullable=False),
            Column("commission", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def create_table(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.TABLE_NAME):
            metadata = MetaData(engine)
            self.get_table(metadata)
            metadata.create_all(engine)

    def add_transaction(
        self, engine: MockConnection, transaction: DbAddTransactionIn
    ) -> DbAddTransactionIn:
        metadata = MetaData(engine)
        tbl = self.get_table(metadata)
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
        # TODO get execute response from that
        return transaction

    def fetch_user_transactions(
        self, engine: MockConnection, api_key: str
    ) -> DbUserTransactionsOutput:
        metadata = MetaData(engine)
        tbl = self.get_table(metadata)
        trx = tbl.select().where(tbl.c.src_api_key == api_key)
        con = engine.connect()
        transactions = con.execute(trx).fetchall()
        return DbUserTransactionsOutput(transactions)
