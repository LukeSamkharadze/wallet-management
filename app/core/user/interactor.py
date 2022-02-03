from dataclasses import dataclass
from app.core import IBTCWalletRepository


@dataclass
class UserInteractor:

    # TODO: add api_key generate, preparing for converting to database object
    def add_user(self, iBTCWalletRepository: IBTCWalletRepository):
        return iBTCWalletRepository.add_user()
