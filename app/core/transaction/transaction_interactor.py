import datetime
from dataclasses import dataclass, field
from typing import Protocol

from app.core import BaseInteractorOutput, DbAddTransactionIn, IBTCWalletRepository
from app.utils.result_codes import ResultCode


@dataclass
class TransactionInput:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float


@dataclass
class TransactionOutput(BaseInteractorOutput):
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    dest_btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class UserTransaction:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class UserTransactionsOutput(BaseInteractorOutput):
    user_transactions: list[UserTransaction] = field(default_factory=list)


class ICommissionCalculator(Protocol):
    def calculate_commission(
        self,
        btc_wallet_repository: IBTCWalletRepository,
        transaction: TransactionInput,
    ) -> float:
        pass


@dataclass
class TransactionInteractor:
    @staticmethod
    def add_transaction(
        btc_wallet_repository: IBTCWalletRepository,
        commission_calculator: ICommissionCalculator,
        transaction: TransactionInput,
    ) -> TransactionOutput:
        commission = commission_calculator.calculate_commission(
            btc_wallet_repository,
            transaction,
        )
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
            dest_btc_amount=us.btc_amount - us.commission,
            commission=us.commission,
            create_date_utc=us.create_date_utc,
            result_code=us.result_code,
        )

    @staticmethod
    def fetch_user_transactions(
        btc_wallet_repository: IBTCWalletRepository, api_key: str
    ) -> UserTransactionsOutput:
        fetch_result = btc_wallet_repository.fetch_user_transactions(api_key)
        if fetch_result.result_code != ResultCode.SUCCESS:
            return UserTransactionsOutput(result_code=fetch_result.result_code)

        transactions = []
        for transaction in fetch_result.user_transactions:
            user_transaction = UserTransaction(
                transaction.src_api_key,
                transaction.src_public_key,
                transaction.dst_public_key,
                transaction.btc_amount,
                transaction.commission,
                transaction.create_date_utc,
            )
            transactions.append(user_transaction)
        return UserTransactionsOutput(
            user_transactions=transactions, result_code=fetch_result.result_code
        )
