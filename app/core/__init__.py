from typing import Protocol


class IBTCWalletRepository(Protocol):
    def add_user(self):
        pass

    def add_wallet(self):
        pass

    def add_transaction(self):
        pass
