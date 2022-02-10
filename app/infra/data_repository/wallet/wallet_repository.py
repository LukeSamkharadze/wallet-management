from dataclasses import dataclass

from sqlalchemy import Column, Date, Float, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import session

from app.app_settings import AppSettings
from app.core import DbAddWalletIn, DbAddWalletOut


@dataclass
class WalletRepository:
    TABLE_NAME: str = "Wallet"

    # TODO add foreign key logic
    def get_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TABLE_NAME,
            metadata,
            Column("Id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("public_key", String, nullable=False),
            Column("btc_amount", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
            Column("Api_key", String, nullable=False),
        )

    def create_table(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.TABLE_NAME):
            metadata = MetaData(engine)
            self.get_table(metadata)
            metadata.create_all(engine)

    def add_wallet(
        self, engine: MockConnection, wallet: DbAddWalletIn
    ) -> DbAddWalletIn:
        metadata = MetaData(engine)
        tbl = self.get_table(metadata)
        ins = tbl.insert().values(
            Api_key=wallet.api_key,
            create_date_utc=wallet.create_date_utc,
            public_key=wallet.public_key,
            btc_amount=wallet.btc_amount,
        )
        con = engine.connect()
        con.execute(ins)
        # TODO get execute response from that
        return wallet

    def update_wallet_balance(
        self, engine: MockConnection, public_key: str, amount: float
    ) -> int:
        metadata = MetaData(engine)
        walletTable = self.get_table(metadata)
        # TODO make table update and return status code
        return 1

    # wallet = (
    #      session.query(walletTable)
    #      .filter(walletTable.public_key == public_key)
    #      .one()
    #  )
    # session.commit()

    def count_wallets_of_user(self, engine: MockConnection, Api_key: str) -> int:

        metadata = MetaData(engine)
        walletTable = self.get_table(metadata)
        query = walletTable.select().where(walletTable.c.Api_key == Api_key)
        con = engine.connect()
        wallets = con.execute(query)
        # TODO use sqlalchemy count() for this
        count = 0
        for sd in wallets:
            count += 1

        return count
