from dataclasses import dataclass

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
    select,
)
from sqlalchemy.engine.mock import MockConnection

from app.core import (
    DbAddWalletIn,
    DbAddWalletOut,
    DbGetUserWalletCountIn,
    DbGetUserWalletCountOut,
    DbGetWalletIn,
    DbGetWalletOut,
    DbUpdateWalletBalanceIn,
    DbUpdateWalletBalanceOut,
)
from app.utils.result_codes import ResultCode


@dataclass
class WalletRepository:
    WALLETS_TABLE_NAME: str = "wallets"

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
    ) -> DbAddWalletOut:
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
        return DbAddWalletOut(
            create_date_utc=wallet.create_date_utc,
            api_key=wallet.api_key,
            public_key=wallet.public_key,
            btc_amount=wallet.btc_amount,
            result_code=ResultCode.SUCCESS,
        )

    def update_wallet_balance(
        self, engine: MockConnection, update_input: DbUpdateWalletBalanceIn
    ) -> DbUpdateWalletBalanceOut:
        metadata = MetaData(engine)
        tbl = self.get_table(metadata)
        query = tbl.select().where(tbl.c.public_key == update_input.public_key)
        wallet = engine.execute(query).one()
        query = (
            tbl.update()
            .where(tbl.c.public_key == update_input.public_key)
            .values(btc_amount=wallet.btc_amount + update_input.amount)
        )
        engine.execute(query)
        return DbUpdateWalletBalanceOut(result_code=ResultCode.SUCCESS)

    def get_wallet(
        self, engine: MockConnection, wallet: DbGetWalletIn
    ) -> DbGetWalletOut:
        metadata = MetaData(engine)
        wallet_table = self.get_table(metadata)
        query = wallet_table.select().where(
            wallet_table.c.public_key == wallet.public_key,
        )
        con = engine.connect()
        wallets = con.execute(query).fetchall()

        if len(wallets) != 1:
            return DbGetWalletOut(result_code=ResultCode.WALLET_NOT_FOUND)

        return DbGetWalletOut(
            result_code=ResultCode.SUCCESS,
            btc_amount=wallets[0]["btc_amount"],
            public_key=wallets[0]["public_key"],
            api_key=wallets[0]["api_key"],
        )

    def count_wallets_of_user(
        self, engine: MockConnection, count_input: DbGetUserWalletCountIn
    ) -> DbGetUserWalletCountOut:
        metadata = MetaData(engine)
        wallet_table = self.get_table(metadata)
        count = (
            select([func.count()])
            .select_from(wallet_table)
            .where(
                wallet_table.c.api_key == count_input.api_key,
            )
            .scalar()
        )
        return DbGetUserWalletCountOut(
            wallet_count=count, result_code=ResultCode.SUCCESS
        )
