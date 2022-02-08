import datetime
from dataclasses import dataclass

from app.core import IBTCWalletRepository
from app.infra.in_memory import TransactionInMemoryIn


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


@dataclass
class TransactionInteractor:
    def add_transaction(
        self, btc_wallet_repository: IBTCWalletRepository, transaction: TransactionInput
    ) -> TransactionOutput:

        # TODO statistic update and wallet amount update logic
        commission = transaction.btc_amount * 0.015
        create_date_utc = datetime.datetime.now()
        us = btc_wallet_repository.add_transaction(
            TransactionInMemoryIn(
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
