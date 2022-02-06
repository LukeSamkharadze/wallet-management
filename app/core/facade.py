from dataclasses import dataclass

from app.core import IBTCWalletRepository
from app.core.transaction.interactor import TransactionInput, TransactionInteractor
from app.core.user.interactor import UserInput, UserInteractor
from app.core.wallet.interactor import WalletInput, WalletInteractor


@dataclass
class BTCWalletCore:
    iBTCWalletRepository: IBTCWalletRepository
    user_interactor: UserInteractor
    wallet_interactor: WalletInteractor
    transaction_interactor: TransactionInteractor

    @classmethod
    def create(cls, iBTCWalletRepository: IBTCWalletRepository) -> "BTCWalletCore":
        return cls(
            iBTCWalletRepository=iBTCWalletRepository,
            user_interactor=UserInteractor(),
            wallet_interactor=WalletInteractor(),
            transaction_interactor=TransactionInteractor(),
        )

    def add_user(self, user: UserInput):
        return self.user_interactor.add_user(
            iBTCWalletRepository=self.iBTCWalletRepository, user=user
        )

    def add_wallet(self, wallet: WalletInput):
        return self.wallet_interactor.add_wallet(
            iBTCWalletRepository=self.iBTCWalletRepository, wallet=wallet
        )

    def fetch_wallet(self):
        pass

    def add_transaction(self, transaction: TransactionInput):
        return self.transaction_interactor.add_transaction(
            iBTCWalletRepository=self.iBTCWalletRepository, transaction=transaction
        )
