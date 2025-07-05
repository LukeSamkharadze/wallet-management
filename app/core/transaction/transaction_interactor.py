import datetime
from dataclasses import dataclass, field
from typing import Protocol

from app.app_settings import AppSettings
from app.core import (
    BaseInteractorOutput,
    DbAddTransactionIn,
    DbFetchStatisticsIn,
    DbGetWalletIn,
    IWalletRepository,
)
from app.core.crypto_market_api.multi_currency_api import CryptoCurrency
from app.core.wallet.wallet_interactor import StatisticsOutput
from app.utils.result_codes import ResultCode


@dataclass
class TransactionInput:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    amount: float
    currency: str = ""


@dataclass
class TransactionOutput(BaseInteractorOutput):
    src_api_key: str = ""
    src_public_key: str = ""
    dst_public_key: str = ""
    amount: float = 0
    dest_amount: float = 0
    currency: str = ""
    commission: float = 0
    create_date_utc: datetime.datetime = datetime.datetime.now()


@dataclass
class UserTransaction:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    amount: float
    currency: str
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class UserTransactionsOutput(BaseInteractorOutput):
    user_transactions: list[UserTransaction] = field(default_factory=list)


class ICommissionCalculator(Protocol):
    def calculate_commission(
        self,
        wallet_repository: IWalletRepository,
        transaction: TransactionInput,
        currency: str,
    ) -> float:
        pass


@dataclass
class TransactionInteractor:
    @staticmethod
    def add_transaction(
        wallet_repository: IWalletRepository,
        commission_calculator: ICommissionCalculator,
        transaction: TransactionInput,
    ) -> TransactionOutput:
        src_wallet = wallet_repository.fetch_wallet(
            DbGetWalletIn(public_key=transaction.src_public_key)
        )
        if src_wallet.result_code != ResultCode.SUCCESS:
            return TransactionOutput(result_code=src_wallet.result_code)
        
        dst_wallet = wallet_repository.fetch_wallet(
            DbGetWalletIn(public_key=transaction.dst_public_key)
        )
        if dst_wallet.result_code != ResultCode.SUCCESS:
            return TransactionOutput(result_code=dst_wallet.result_code)
        
        if src_wallet.currency != dst_wallet.currency:
            return TransactionOutput(result_code=ResultCode.CURRENCY_MISMATCH)
        
        currency = src_wallet.currency
        
        currency_enum = CryptoCurrency.from_symbol(currency)
        if not currency_enum:
            return TransactionOutput(result_code=ResultCode.INVALID_CURRENCY)
        
        commission = commission_calculator.calculate_commission(
            wallet_repository,
            transaction,
            currency,
        )
        create_date_utc = datetime.datetime.now()
        us = wallet_repository.add_transaction(
            DbAddTransactionIn(
                src_api_key=transaction.src_api_key,
                src_public_key=transaction.src_public_key,
                dst_public_key=transaction.dst_public_key,
                amount=transaction.amount,
                currency=currency,
                commission=commission,
                create_date_utc=create_date_utc,
            )
        )

        return TransactionOutput(
            src_api_key=us.src_api_key,
            src_public_key=us.src_public_key,
            dst_public_key=us.dst_public_key,
            amount=us.amount,
            dest_amount=us.amount - us.commission,
            currency=us.currency,
            commission=us.commission,
            create_date_utc=us.create_date_utc,
            result_code=us.result_code,
        )

    @staticmethod
    def fetch_user_transactions(
        wallet_repository: IWalletRepository, api_key: str
    ) -> UserTransactionsOutput:
        fetch_result = wallet_repository.fetch_user_transactions(api_key)
        if fetch_result.result_code != ResultCode.SUCCESS:
            return UserTransactionsOutput(result_code=fetch_result.result_code)

        transactions = []
        for transaction in fetch_result.user_transactions:
            user_transaction = UserTransaction(
                transaction.src_api_key,
                transaction.src_public_key,
                transaction.dst_public_key,
                transaction.amount,
                transaction.currency,
                transaction.commission,
                transaction.create_date_utc,
            )
            transactions.append(user_transaction)
        return UserTransactionsOutput(
            user_transactions=transactions, result_code=fetch_result.result_code
        )

    @staticmethod
    def fetch_statistics(
        wallet_repository: IWalletRepository, 
        admin_api_key: str,
        currency: str = "",
    ) -> StatisticsOutput:
        if (
            admin_api_key
            != AppSettings().get_config()["meta_information"]["admin_api_key"]
        ):
            return StatisticsOutput(result_code=ResultCode.REQUIRES_ADMIN_PRIVILEGES)

        result = wallet_repository.fetch_statistics(DbFetchStatisticsIn(currency=currency))
        return StatisticsOutput(
            commissions_sum=result.commissions_sum,
            transactions_total_amount=result.transactions_total_amount,
            currency=result.currency,
            result_code=result.result_code,
        )
