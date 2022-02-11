from dataclasses import dataclass

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection

from app.core import DbAddWalletIn, DbGetWalletIn, DbGetWalletOut
from app.utils.result_codes import ResultCode


@dataclass
class WalletRepository:
    WALLETS_TABLE_NAME: str = "wallets"

    # TODO add foreign key logic
    def get_table(self, metadata: MetaData) -> Table:
        return Table(
            self.WALLETS_TABLE_NAME,
            metadata,
            Column("id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("public_key", String, nullable=False),
            Column("btc_amount", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
            Column("api_key", String, ForeignKey("users.api_key"), nullable=False),
        )

    def create_tables(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.WALLETS_TABLE_NAME):
            metadata = MetaData(engine)
            metadata.reflect()
            self.get_table(metadata)
            metadata.create_all(engine)

    def add_wallet(
        self, engine: MockConnection, wallet: DbAddWalletIn
    ) -> DbAddWalletIn:
        metadata = MetaData(engine)
        tbl = self.get_table(metadata)
        ins = tbl.insert().values(
            api_key=wallet.api_key,
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
        self.get_table(metadata)
        # TODO make table update and return status code
        return 1

    # wallet = (
    #      session.query(walletTable)
    #      .filter(walletTable.public_key == public_key)
    #      .one()
    #  )
    # session.commit()

    def get_wallet(
        self, engine: MockConnection, wallet: DbGetWalletIn
    ) -> DbGetWalletOut:
        metadata = MetaData(engine)
        wallet_table = self.get_table(metadata)
        query = wallet_table.select().where(
            wallet_table.c.api_key == wallet.api_key
            and wallet_table.c.address == wallet.public_key
        )
        con = engine.connect()
        wallets = con.execute(query).fetchall()

        if len(wallets) != 1:
            return DbGetWalletOut(result_code=ResultCode.WALLET_NOT_FOUND)

        return DbGetWalletOut(
            result_code=ResultCode.SUCCESS,
            btc_amount=wallets[0]["btc_amount"],
            public_key=wallets[0]["public_key"],
        )

    def count_wallets_of_user(self, engine: MockConnection, api_key: str) -> int:
        metadata = MetaData(engine)
        wallet_table = self.get_table(metadata)
        query = wallet_table.select().where(wallet_table.c.api_key == api_key)
        con = engine.connect()
        wallets = con.execute(query)
        # TODO use sqlalchemy count() for this
        count = 0
        for sd in wallets:
            count += 1

        return count
