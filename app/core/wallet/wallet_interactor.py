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
    IWalletRepository,
)
from app.core.crypto_market_api import ICryptoMarketApi
from app.core.crypto_market_api.multi_currency_api import CryptoCurrency
from app.utils.result_codes import ResultCode


@dataclass
class FetchWalletInput:
    api_key: str
    address: str


@dataclass
class FetchWalletOutput(BaseInteractorOutput):
    address: str = ""
    balance: float = 0
    currency: str = ""
    usd_balance: float = 0


@dataclass
class AddWalletInput:
    api_key: str
    currency: str


@dataclass
class AddWalletOutput(BaseInteractorOutput):
    api_key: str = ""
    create_date_utc: datetime.datetime = datetime.datetime.now()
    public_key: str = ""
    amount: float = 0
    currency: str = ""
    usd_balance: float = 0


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
class WalletTransactionsOutput(BaseInteractorOutput):
    wallet_transactions: list[UserTransaction] = field(default_factory=list)


@dataclass
class StatisticsOutput(BaseInteractorOutput):
    commissions_sum: float = 0
    transactions_total_amount: int = 0
    currency: str = ""


@dataclass
class WalletInteractor:
    @staticmethod
    def add_wallet(
        wallet_repository: IWalletRepository,
        crypto_market_api: ICryptoMarketApi,
        wallet: AddWalletInput
    ) -> AddWalletOutput:
        currency_enum = CryptoCurrency.from_symbol(wallet.currency)
        if not currency_enum:
            return AddWalletOutput(result_code=ResultCode.INVALID_CURRENCY)
        
        public_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        
        count_result = wallet_repository.count_wallets_of_user(
            DbGetUserWalletCountIn(wallet.api_key, wallet.currency)
        )
        config = AppSettings().get_config()
        if count_result.wallet_count >= int(
            config.get("wallet", "max_wallet_per_user")
        ):
            return AddWalletOutput(result_code=ResultCode.WALLET_LIMIT_PER_USER_REACHED)

        initial_deposit_btc = float(config.get("wallet", "new_wallet_deposit_btc"))
        
        if wallet.currency == "BTC":
            initial_amount = initial_deposit_btc
        else:
            btc_price = crypto_market_api.get_crypto_price(CryptoCurrency.BTC)
            target_price = crypto_market_api.get_crypto_price(currency_enum)
            
            if btc_price and target_price:
                btc_usd_value = initial_deposit_btc * btc_price.usd_price
                initial_amount = btc_usd_value / target_price.usd_price
            else:
                initial_amount = 1.0

        us = wallet_repository.add_wallet(
            DbAddWalletIn(
                api_key=wallet.api_key,
                create_date_utc=create_date_utc,
                public_key=public_key,
                amount=initial_amount,
                currency=wallet.currency,
            )
        )

        usd_balance = 0
        if us.result_code == ResultCode.SUCCESS:
            price_data = crypto_market_api.get_crypto_price(currency_enum)
            if price_data:
                usd_balance = initial_amount * price_data.usd_price

        return AddWalletOutput(
            api_key=us.api_key,
            create_date_utc=us.create_date_utc,
            public_key=us.public_key,
            amount=us.amount,
            currency=us.currency,
            usd_balance=usd_balance,
            result_code=us.result_code,
        )

    @staticmethod
    def update_wallet_balance(
        wallet_repository: IWalletRepository, public_key: str, amount: float
    ) -> ResultCode:
        return wallet_repository.update_wallet_balance(
            DbUpdateWalletBalanceIn(public_key=public_key, amount=amount)
        ).result_code

    @staticmethod
    def fetch_wallet(
        wallet_repository: IWalletRepository,
        crypto_market_api: ICryptoMarketApi,
        wallet_input: FetchWalletInput,
    ) -> FetchWalletOutput:
        result = wallet_repository.fetch_wallet(
            DbGetWalletIn(public_key=wallet_input.address)
        )
        if result.result_code != ResultCode.SUCCESS:
            return FetchWalletOutput(result_code=result.result_code)

        if result.api_key != wallet_input.api_key:
            return FetchWalletOutput(result_code=ResultCode.WALLET_NOT_ACCESSIBLE)

        currency_enum = CryptoCurrency.from_symbol(result.currency)
        usd_balance = 0
        if currency_enum:
            price_data = crypto_market_api.get_crypto_price(currency_enum)
            if price_data:
                usd_balance = result.amount * price_data.usd_price
        
        return FetchWalletOutput(
            result_code=result.result_code,
            balance=result.amount,
            currency=result.currency,
            address=result.public_key,
            usd_balance=usd_balance,
        )

    @staticmethod
    def fetch_wallet_transactions(
        wallet_repository: IWalletRepository, address: str, api_key: str
    ) -> WalletTransactionsOutput:
        fetch_result = wallet_repository.fetch_wallet_transactions(address, api_key)
        if fetch_result.result_code != ResultCode.SUCCESS:
            return WalletTransactionsOutput(result_code=fetch_result.result_code)

        transactions = []
        for transaction in fetch_result.wallet_transactions:
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
        return WalletTransactionsOutput(
            wallet_transactions=transactions, result_code=fetch_result.result_code
        )
