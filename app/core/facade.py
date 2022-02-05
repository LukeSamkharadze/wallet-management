from dataclasses import dataclass
from app.core import IBTCWalletRepository

from app.core.user.interactor import (
    UserInteractor,
)
from app.core.user.interactor import UserInput
from app.infra.in_memory import BTCWalletInMemoryRepository, UserInMemoryRepository


@dataclass
class BTCWalletCore:
    iBTCWalletRepository: IBTCWalletRepository
    user_interactor: UserInteractor

    @classmethod
    def create(cls, iBTCWalletRepository: IBTCWalletRepository) -> "BTCWalletCore":
        return cls(
            iBTCWalletRepository=iBTCWalletRepository,
            user_interactor=UserInteractor(),
        )

    def add_user(self, user: UserInput):
        return self.user_interactor.add_user(
            iBTCWalletRepository=self.iBTCWalletRepository,
            user=user
        )
