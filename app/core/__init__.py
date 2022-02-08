from typing import Protocol

from app.infra.in_memory import TransactionInMemoryIn, UserInMemoryIn, WalletInMemoryIn


class IBTCWalletRepository(Protocol):
    def add_user(self, user: UserInMemoryIn) -> UserInMemoryIn:
        pass

    def add_wallet(self, wallet: WalletInMemoryIn) -> WalletInMemoryIn:
        pass

    def add_transaction(
        self, transaction: TransactionInMemoryIn
    ) -> TransactionInMemoryIn:
        pass
