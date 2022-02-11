import datetime
import uuid
from dataclasses import dataclass

from app.app_settings import AppSettings
from app.core import DbAddWalletIn, IBTCWalletRepository


@dataclass
class WalletInput:
    api_key: str


@dataclass
class WalletOutput:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float
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
class WalletTransactionsOutput:
    wallet_transactions: list[UserTransaction]
    result_code: int = 0


@dataclass
class WalletInteractor:
    @staticmethod
    def add_wallet(
        btc_wallet_repository: IBTCWalletRepository, wallet: WalletInput
    ) -> WalletOutput:

        public_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        walletsCount = btc_wallet_repository.count_wallets_of_user(wallet.api_key)
        if walletsCount >= int(
            AppSettings().get_config().get("wallet", "max_wallet_per_user")
        ):
            return WalletOutput(
                api_key=wallet.api_key,
                create_date_utc=create_date_utc,
                public_key=public_key,
                btc_amount=-1,
            )
        us = btc_wallet_repository.add_wallet(
            DbAddWalletIn(
                api_key=wallet.api_key,
                create_date_utc=create_date_utc,
                public_key=public_key,
                btc_amount=0,
            )
        )

        return WalletOutput(
            api_key=us.api_key,
            create_date_utc=us.create_date_utc,
            public_key=us.public_key,
            btc_amount=us.btc_amount,
        )

    @staticmethod
    def update_wallet_balance(
        btc_wallet_repository: IBTCWalletRepository, public_key: str, amount: float
    ) -> int:
        return btc_wallet_repository.update_wallet_balance(public_key, amount)

    @staticmethod
    def fetch_wallet_transactions(
        btc_wallet_repository: IBTCWalletRepository, address: str, api_key: str
    ) -> WalletTransactionsOutput:
        transactions = []
        for transaction in btc_wallet_repository.fetch_wallet_transactions(
            address, api_key
        ).wallet_transactions:
            user_transaction = UserTransaction(
                transaction.src_api_key,
                transaction.src_public_key,
                transaction.dst_public_key,
                transaction.btc_amount,
                transaction.commission,
                transaction.create_date_utc,
            )
            transactions.append(user_transaction)
        return WalletTransactionsOutput(transactions)
