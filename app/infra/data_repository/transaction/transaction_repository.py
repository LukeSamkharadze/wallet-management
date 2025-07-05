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
            Column("amount", Float, nullable=False),
            Column("currency", String, nullable=False),
            Column("commission", Float, nullable=False),
            Column("create_date_utc", Date, nullable=False),
        )

    def get_transaction_stats_table(self, metadata: MetaData) -> Table:
        return Table(
            self.TRANSACTIONS_STATS_TABLE_NAME,
            metadata,
            Column("id", Integer, primary_key=True, nullable=False, autoincrement=True),
            Column("commission_sum", Float, nullable=False),
            Column("currency", String, nullable=False),
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
            amount=transaction.amount,
            currency=transaction.currency,
            commission=transaction.commission,
            create_date_utc=transaction.create_date_utc,
        )
        con = engine.connect()
        con.execute(ins)
        return DbAddTransactionOut(
            commission=transaction.commission,
            create_date_utc=transaction.create_date_utc,
            src_api_key=transaction.src_api_key,
            src_public_key=transaction.src_public_key,
            dst_public_key=transaction.dst_public_key,
            amount=transaction.amount,
            currency=transaction.currency,
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
        
        transaction_objects = []
        for trans in transactions:
            transaction_objects.append(
                DbAddTransactionOut(
                    src_api_key=trans["src_api_key"],
                    src_public_key=trans["src_public_key"],
                    dst_public_key=trans["dst_public_key"],
                    amount=trans["amount"],
                    currency=trans["currency"],
                    commission=trans["commission"],
                    create_date_utc=trans["create_date_utc"],
                    result_code=ResultCode.SUCCESS,
                )
            )
        
        return DbUserTransactionsOutput(
            user_transactions=transaction_objects, result_code=ResultCode.SUCCESS
        )

    def update_commission_stats(
        self, engine: MockConnection, commission: DbUpdateCommissionStatsIn
    ) -> DbUpdateCommissionStatsOut:
        commission_date = commission.create_date_utc.date()
        metadata = MetaData(engine)
        stats_table = self.get_transaction_stats_table(metadata)
        query = stats_table.select().where(
            (stats_table.c.stat_date_utc == commission_date) &
            (stats_table.c.currency == commission.currency)
        )
        con = engine.connect()
        stat = con.execute(query).first()

        if not stat:
            new_row = stats_table.insert().values(
                commission_sum=commission.commission_amount,
                currency=commission.currency,
                stat_date_utc=commission_date,
                total_transactions=1,
            )
            con.execute(new_row)
        else:
            update_row = (
                stats_table.update()
                .values(
                    commission_sum=(
                        stats_table.c.commission_sum
                        + commission.commission_amount
                    ),
                    total_transactions=(stats_table.c.total_transactions + 1),
                )
                .where(
                    (stats_table.c.stat_date_utc == commission_date) &
                    (stats_table.c.currency == commission.currency)
                )
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
        
        transaction_objects = []
        for trans in transactions:
            transaction_objects.append(
                DbAddTransactionOut(
                    src_api_key=trans["src_api_key"],
                    src_public_key=trans["src_public_key"],
                    dst_public_key=trans["dst_public_key"],
                    amount=trans["amount"],
                    currency=trans["currency"],
                    commission=trans["commission"],
                    create_date_utc=trans["create_date_utc"],
                    result_code=ResultCode.SUCCESS,
                )
            )
        
        return DbWalletTransactionsOutput(
            wallet_transactions=transaction_objects, result_code=ResultCode.SUCCESS
        )

    def fetch_transaction_statistics(
        self, engine: MockConnection, stats_input: DbFetchStatisticsIn
    ) -> DbFetchStatisticsOut:
        metadata = MetaData(engine)
        stats_table = self.get_transaction_stats_table(metadata)
        
        if stats_input.currency:
            query = stats_table.select().where(stats_table.c.currency == stats_input.currency)
        else:
            query = stats_table.select()
            
        con = engine.connect()
        transaction_stats = con.execute(query).fetchall()
        
        return DbFetchStatisticsOut(
            result_code=ResultCode.SUCCESS,
            commissions_sum=sum(
                tran.commission_sum for tran in transaction_stats
            ),
            transactions_total_amount=sum(
                tran.total_transactions for tran in transaction_stats
            ),
            currency=stats_input.currency,
        )
