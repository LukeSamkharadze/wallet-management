from dataclasses import dataclass

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, MetaData, String, Table
from sqlalchemy.engine.mock import MockConnection

from app.core import (
    DbAddTransactionIn,
    DbAddTransactionOut,
    DbFetchStatisticsIn,
    DbFetchStatisticsOut,
    DbUpdateCommissionStatsIn,
    DbUpdateCommissionStatsOut,
    DbUserTransactionsOutput,
    DbWalletTransactionsOutput,
)
from app.utils.result_codes import ResultCode


@dataclass
class TransactionRepository:
    TRANSACTIONS_TABLE_NAME: str = "transactions"
    TRANSACTIONS_STATS_TABLE_NAME: str = "transaction_stats"

    # TODO add foreign key logic
    def get_transactions_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TRANSACTIONS_TABLE_NAME,
            metadata,
            Column("id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("src_api_key", String, ForeignKey("users.api_key"), nullable=False),
            Column(
                "src_public_key",
                String,
                ForeignKey("wallets.public_key"),
                nullable=False,
            ),
            Column(
                "dst_public_key",
                String,
                ForeignKey("wallets.public_key"),
                nullable=False,
            ),
            Column("btc_amount", Float, nullable=False),
            Column("commission", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def get_transaction_stats_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TRANSACTIONS_STATS_TABLE_NAME,
            metadata,
            Column("id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("commission_sum_btc", Float, nullable=False),
            Column("total_transactions", Integer, nullable=False),
            Column("stat_date_utc", Date, nullable=False),
        )

    def create_tables(self, engine: MockConnection) -> None:
        if not engine.dialect.has_table(engine.connect(), self.TRANSACTIONS_TABLE_NAME):
            metadata = MetaData(engine)
            metadata.reflect()
            self.get_transactions_table(metadata)
            metadata.create_all(engine)

        if not engine.dialect.has_table(
            engine.connect(), self.TRANSACTIONS_STATS_TABLE_NAME
        ):
            metadata = MetaData(engine)
            metadata.reflect()
            self.get_transaction_stats_table(metadata)
            metadata.create_all(engine)

    def add_transaction(
        self, engine: MockConnection, transaction: DbAddTransactionIn
    ) -> DbAddTransactionOut:
        metadata = MetaData(engine)
        tbl = self.get_transactions_table(metadata)
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
        return DbAddTransactionOut(
            commission=transaction.commission,
            create_date_utc=transaction.create_date_utc,
            src_api_key=transaction.src_api_key,
            src_public_key=transaction.src_public_key,
            dst_public_key=transaction.dst_public_key,
            btc_amount=transaction.btc_amount,
            result_code=ResultCode.SUCCESS,
        )

    def fetch_user_transactions(
        self, engine: MockConnection, api_key: str
    ) -> DbUserTransactionsOutput:
        metadata = MetaData(engine)
        tbl = self.get_transactions_table(metadata)
        trx = tbl.select().where(tbl.c.src_api_key == api_key)
        con = engine.connect()
        transactions = con.execute(trx).fetchall()
        return DbUserTransactionsOutput(
            user_transactions=transactions, result_code=ResultCode.SUCCESS
        )

    def update_commission_stats(
        self, engine: MockConnection, commission: DbUpdateCommissionStatsIn
    ) -> DbUpdateCommissionStatsOut:
        commission_date = commission.create_date_utc.date()
        metadata = MetaData(engine)
        stats_table = self.get_transaction_stats_table(metadata)
        query = stats_table.select().where(
            stats_table.c.stat_date_utc == commission_date
        )
        con = engine.connect()
        stat = con.execute(query).first()

        if not stat:
            new_row = stats_table.insert().values(
                commission_sum_btc=commission.commission_amount_btc,
                stat_date_utc=commission_date,
                total_transactions=1,
            )
            con.execute(new_row)
        else:
            update_row = (
                stats_table.update()
                .values(
                    commission_sum_btc=(
                        stats_table.c.commission_sum_btc
                        + commission.commission_amount_btc
                    ),
                    total_transactions=(stats_table.c.total_transactions + 1),
                )
                .where(stats_table.c.stat_date_utc == commission_date)
            )
            con.execute(update_row)
        return DbUpdateCommissionStatsOut(result_code=ResultCode.SUCCESS)

    def fetch_wallet_transactions(
        self, engine: MockConnection, address: str, api_key: str
    ) -> DbWalletTransactionsOutput:
        metadata = MetaData(engine)
        tbl = self.get_transactions_table(metadata)
        trx = (
            tbl.select()
            .where(tbl.c.src_api_key == api_key)
            .where(tbl.c.src_public_key == address)
        )
        con = engine.connect()
        transactions = con.execute(trx).fetchall()
        return DbWalletTransactionsOutput(
            wallet_transactions=transactions, result_code=ResultCode.SUCCESS
        )

    def fetch_transaction_statistics(
        self, engine: MockConnection, stats_input: DbFetchStatisticsIn
    ) -> DbFetchStatisticsOut:
        metadata = MetaData(engine)
        stats_table = self.get_transaction_stats_table(metadata)
        query = stats_table.select().where()
        con = engine.connect()
        transaction_stats = con.execute(query).fetchall()
        return DbFetchStatisticsOut(
            result_code=ResultCode.SUCCESS,
            commissions_sum_btc=sum(
                tran.commission_sum_btc for tran in transaction_stats
            ),
            transactions_total_amount=sum(
                tran.total_transactions for tran in transaction_stats
            ),
        )
