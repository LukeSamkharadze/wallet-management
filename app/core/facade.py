from dataclasses import dataclass

from app.app_settings import AppSettings
from app.core import IBTCWalletRepository
from app.core.crypto_market_api import ICryptoMarketApi
from app.core.observables.transaction_observables import (
    TransactionCreatedData,
    TransactorObservable,
)
from app.core.transaction.transaction_interactor import (
    ICommissionCalculator,
    TransactionInput,
    TransactionInteractor,
    TransactionOutput,
    UserTransactionsOutput,
)
from app.core.user.user_interactor import UserInput, UserInteractor, UserOutput
from app.core.wallet.wallet_interactor import (
    AddWalletInput,
    AddWalletOutput,
    FetchWalletInput,
    FetchWalletOutput,
    WalletInteractor,
    WalletTransactionsOutput,
)


class DefaultCommissionCalculator(ICommissionCalculator):
    def calculate_commission(
        self,
        btc_wallet_repository: IBTCWalletRepository,
        transaction: TransactionInput,
    ) -> float:
        app_config = AppSettings().get_config()
        commission_fraction = float(app_config["transaction"]["commission_fraction"])

        commission = transaction.btc_amount * commission_fraction
        # TODO: RETURN 0, IF BOTH PUBLIC KEYS ARE OF THE SAME USER
        return commission


@dataclass
class BTCWalletCore(TransactorObservable):
    btc_wallet_repository: IBTCWalletRepository
    crypto_market_api: ICryptoMarketApi

    @classmethod
    def create(
        cls,
        btc_wallet_repository: IBTCWalletRepository,
        crypto_market_api: ICryptoMarketApi,
    ) -> "BTCWalletCore":
        return cls(
            btc_wallet_repository=btc_wallet_repository,
            crypto_market_api=crypto_market_api,
        )

    def add_user(self, user: UserInput) -> UserOutput:

        return UserInteractor.add_user(
            btc_wallet_repository=self.btc_wallet_repository, user=user
        )

    def add_wallet(self, wallet: AddWalletInput) -> AddWalletOutput:
        return WalletInteractor.add_wallet(
            btc_wallet_repository=self.btc_wallet_repository, wallet=wallet
        )

    def fetch_wallet(
        self,
        wallet_input: FetchWalletInput,
    ) -> FetchWalletOutput:
        return WalletInteractor.fetch_wallet(
            self.btc_wallet_repository, self.crypto_market_api, wallet_input
        )

    def add_transaction(self, transaction: TransactionInput) -> TransactionOutput:
        trans = TransactionInteractor.add_transaction(
            btc_wallet_repository=self.btc_wallet_repository,
            commission_calculator=DefaultCommissionCalculator(),
            transaction=transaction,
        )

        # TODO check trans result code
        WalletInteractor.update_wallet_balance(
            self.btc_wallet_repository,
            trans.src_public_key,
            trans.btc_amount * (-1),
        )
        WalletInteractor.update_wallet_balance(
            self.btc_wallet_repository,
            trans.dst_public_key,
            trans.dest_btc_amount,
        )

        self.notify_transaction_created(
            self.btc_wallet_repository,
            TransactionCreatedData(commission_btc=trans.commission),
        )

        return trans

    def fetch_user_transactions(self, api_key: str) -> UserTransactionsOutput:
        return TransactionInteractor.fetch_user_transactions(
            btc_wallet_repository=self.btc_wallet_repository, api_key=api_key
        )

    def fetch_wallet_transactions(
        self, address: str, api_key: str
    ) -> WalletTransactionsOutput:
        return WalletInteractor.fetch_wallet_transactions(
            btc_wallet_repository=self.btc_wallet_repository,
            address=address,
            api_key=api_key,
        )
