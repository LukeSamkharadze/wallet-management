import datetime
import uuid
from dataclasses import dataclass
from app.core import IBTCWalletRepository
from app.infra.in_memory import WalletInMemoryIn


@dataclass
class WalletInput:
    api_key: str


@dataclass
class WalletOutput:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float


@dataclass
class WalletInteractor:
    def add_wallet(
        self, iBTCWalletRepository: IBTCWalletRepository, wallet: WalletInput
    ):

        public_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        us = iBTCWalletRepository.add_wallet(
            WalletInMemoryIn(
                api_key=wallet.api_key,
                create_date_utc=create_date_utc,
                public_key=public_key,
                btc_amount=0,
            )
        )

        return WalletOutput(
            api_key=us.api_key,
            create_date_utc=us.create_date_utc,
            public_key=us.public_key,
            btc_amount=us.btc_amount,
        )
