from dataclasses import dataclass

from app.core import IBTCWalletRepository
from app.core.transaction.interactor import (
    TransactionInput,
    TransactionInteractor,
    TransactionOutput,
)
from app.core.user.interactor import UserInput, UserInteractor, UserOutput
from app.core.wallet.interactor import WalletInput, WalletInteractor, WalletOutput


@dataclass
class BTCWalletCore:
    btc_wallet_repository: IBTCWalletRepository
    user_interactor: UserInteractor
    wallet_interactor: WalletInteractor
    transaction_interactor: TransactionInteractor

    @classmethod
    def create(cls, btc_wallet_repository: IBTCWalletRepository) -> "BTCWalletCore":
        return cls(
            btc_wallet_repository=btc_wallet_repository,
            user_interactor=UserInteractor(),
            wallet_interactor=WalletInteractor(),
            transaction_interactor=TransactionInteractor(),
        )

    def add_user(self, user: UserInput) -> UserOutput:
        return self.user_interactor.add_user(
            btc_wallet_repository=self.btc_wallet_repository, user=user
        )

    def add_wallet(self, wallet: WalletInput) -> WalletOutput:
        return self.wallet_interactor.add_wallet(
            btc_wallet_repository=self.btc_wallet_repository, wallet=wallet
        )

    def fetch_wallet(self) -> None:
        pass

    def add_transaction(self, transaction: TransactionInput) -> TransactionOutput:
        return self.transaction_interactor.add_transaction(
            btc_wallet_repository=self.btc_wallet_repository, transaction=transaction
        )
