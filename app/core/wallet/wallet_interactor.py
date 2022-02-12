import datetime
import uuid
from dataclasses import dataclass, field

from app.app_settings import AppSettings
from app.core import (
    BaseInteractorOutput,
    DbAddWalletIn,
    DbGetUserWalletCountIn,
    DbGetWalletIn,
    DbUpdateWalletBalanceIn,
    IBTCWalletRepository,
)
from app.core.crypto_market_api import ICryptoMarketApi
from app.utils.result_codes import ResultCode


@dataclass
class FetchWalletInput:
    api_key: str
    address: str


@dataclass
class FetchWalletOutput(BaseInteractorOutput):
    address: str = ""
    btc_balance: float = 0
    usd_balance: float = 0


@dataclass
class AddWalletInput:
    api_key: str


@dataclass
class AddWalletOutput(BaseInteractorOutput):
    api_key: str = ""
    create_date_utc: datetime.datetime = datetime.datetime.now()
    public_key: str = ""
    btc_amount: float = 0


@dataclass
class UserTransaction:
    src_api_key: str
    src_public_key: str
    dst_public_key: str
    btc_amount: float
    commission: float
    create_date_utc: datetime.datetime


@dataclass
class WalletTransactionsOutput(BaseInteractorOutput):
    wallet_transactions: list[UserTransaction] = field(default_factory=list)


@dataclass
class WalletInteractor:
    @staticmethod
    def add_wallet(
        btc_wallet_repository: IBTCWalletRepository, wallet: AddWalletInput
    ) -> AddWalletOutput:
        public_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        count_result = btc_wallet_repository.count_wallets_of_user(
            DbGetUserWalletCountIn(wallet.api_key)
        )
        config = AppSettings().get_config()
        if count_result.wallet_count >= int(
            config.get("wallet", "max_wallet_per_user")
        ):
            return AddWalletOutput(result_code=ResultCode.WALLET_LIMIT_PER_USER_REACHED)

        us = btc_wallet_repository.add_wallet(
            DbAddWalletIn(
                api_key=wallet.api_key,
                create_date_utc=create_date_utc,
                public_key=public_key,
                btc_amount=float(config.get("wallet", "new_wallet_deposit_btc")),
            )
        )

        return AddWalletOutput(
            api_key=us.api_key,
            create_date_utc=us.create_date_utc,
            public_key=us.public_key,
            btc_amount=us.btc_amount,
            result_code=us.result_code,
        )

    @staticmethod
    def update_wallet_balance(
        btc_wallet_repository: IBTCWalletRepository, public_key: str, amount: float
    ) -> ResultCode:
        return btc_wallet_repository.update_wallet_balance(
            DbUpdateWalletBalanceIn(public_key=public_key, amount=amount)
        ).result_code

    @staticmethod
    def fetch_wallet(
        btc_wallet_repository: IBTCWalletRepository,
        crypto_market_api: ICryptoMarketApi,
        wallet_input: FetchWalletInput,
    ) -> FetchWalletOutput:
        result = btc_wallet_repository.get_wallet(
            DbGetWalletIn(public_key=wallet_input.address)
        )
        if result.result_code != ResultCode.SUCCESS:
            return FetchWalletOutput(result_code=result.result_code)

        if result.api_key != wallet_input.api_key:
            return FetchWalletOutput(result_code=ResultCode.WALLET_NOT_ACCESSIBLE)

        btc_price_in_usd = crypto_market_api.get_price_of_btc()
        return FetchWalletOutput(
            result_code=result.result_code,
            btc_balance=result.btc_amount,
            address=result.public_key,
            usd_balance=result.btc_amount * btc_price_in_usd,
        )

    @staticmethod
    def fetch_wallet_transactions(
        btc_wallet_repository: IBTCWalletRepository, address: str, api_key: str
    ) -> WalletTransactionsOutput:
        fetch_result = btc_wallet_repository.fetch_wallet_transactions(address, api_key)
        if fetch_result.result_code != ResultCode.SUCCESS:
            return WalletTransactionsOutput(result_code=fetch_result.result_code)

        transactions = []
        for transaction in fetch_result.wallet_transactions:
            user_transaction = UserTransaction(
                transaction.src_api_key,
                transaction.src_public_key,
                transaction.dst_public_key,
                transaction.btc_amount,
                transaction.commission,
                transaction.create_date_utc,
            )
            transactions.append(user_transaction)
        return WalletTransactionsOutput(
            wallet_transactions=transactions, result_code=fetch_result.result_code
        )
