from dataclasses import dataclass

from app.core import IBTCWalletRepository
from app.core.transaction.transaction_interactor import (
    TransactionInput,
    TransactionInteractor,
    TransactionOutput,
    UserTransactionsOutput,
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
        trans = TransactionInteractor.add_transaction(
            btc_wallet_repository=self.btc_wallet_repository, transaction=transaction
        )

        # TODO check trans result code
        WalletInteractor.update_wallet_balace(
            self.btc_wallet_repository, trans.src_public_key, trans.btc_amount * (-1)
        )
        WalletInteractor.update_wallet_balace(
            self.btc_wallet_repository, trans.dst_public_key, trans.btc_amount
        )

        return trans

    def fetch_user_transactions(self, api_key: str) -> UserTransactionsOutput:
        return TransactionInteractor.fetch_user_transactions(
            btc_wallet_repository=self.btc_wallet_repository, api_key=api_key
        )
