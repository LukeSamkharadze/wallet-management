from dataclasses import dataclass

from app.core import IBTCWalletRepository
from app.core.transaction.transaction_interactor import (
    TransactionInput,
    TransactionInteractor,
    TransactionOutput,
)
from app.core.user.user_interactor import UserInput, UserInteractor, UserOutput
from app.core.wallet.wallet_interactor import (
    WalletInput,
    WalletInteractor,
    WalletOutput,
)


@dataclass
class BTCWalletCore:
    btc_wallet_repository: IBTCWalletRepository

    @classmethod
    def create(cls, btc_wallet_repository: IBTCWalletRepository) -> "BTCWalletCore":
        return cls(btc_wallet_repository=btc_wallet_repository,)

    def add_user(self, user: UserInput) -> UserOutput:

        return UserInteractor.add_user(
            btc_wallet_repository=self.btc_wallet_repository, user=user
        )

    def add_wallet(self, wallet: WalletInput) -> WalletOutput:
        return WalletInteractor.add_wallet(
            btc_wallet_repository=self.btc_wallet_repository, wallet=wallet
        )

    def fetch_wallet(self) -> None:
        pass

    def add_transaction(self, transaction: TransactionInput) -> TransactionOutput:
        return TransactionInteractor.add_transaction(
            btc_wallet_repository=self.btc_wallet_repository, transaction=transaction
        )
