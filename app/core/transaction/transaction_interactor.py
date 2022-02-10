import datetime
from dataclasses import dataclass

from app.core import DbAddTransactionIn, IBTCWalletRepository


@dataclass
class TransactionInput:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float


@dataclass
class TransactionOutput:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime
    result_code: int = 0


@dataclass
class UserTransaction:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class UserTransactionsOutput:
    user_transactions: list[UserTransaction]
    result_code: int = 0


@dataclass
class TransactionInteractor:
    def add_transaction(
        btc_wallet_repository: IBTCWalletRepository, transaction: TransactionInput
    ) -> TransactionOutput:

        # TODO statistic update and wallet amount update logic
        commission = transaction.btc_amount * 0.015
        create_date_utc = datetime.datetime.now()
        us = btc_wallet_repository.add_transaction(
            DbAddTransactionIn(
                src_api_key=transaction.src_api_key,
                src_public_key=transaction.src_public_key,
                dst_public_key=transaction.dst_public_key,
                btc_amount=transaction.btc_amount,
                commission=commission,
                create_date_utc=create_date_utc,
            )
        )

        return TransactionOutput(
            src_api_key=us.src_api_key,
            src_public_key=us.src_public_key,
            dst_public_key=us.dst_public_key,
            btc_amount=us.btc_amount,
            commission=us.commission,
            create_date_utc=us.create_date_utc,
        )

    def fetch_user_transactions(
        btc_wallet_repository: IBTCWalletRepository, api_key: str
    ) -> UserTransactionsOutput:
        transactions = []
        for transaction in btc_wallet_repository.fetch_user_transactions(
            api_key
        ).user_transactions:
            user_transaction = UserTransaction(
                transaction.src_api_key,
                transaction.src_public_key,
                transaction.dst_public_key,
                transaction.btc_amount,
                transaction.commission,
                transaction.create_date_utc,
            )
            transactions.append(user_transaction)
        return UserTransactionsOutput(transactions)
