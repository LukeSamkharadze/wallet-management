import datetime
import uuid
from dataclasses import dataclass

from app.core import DbAddWalletIn, IBTCWalletRepository


@dataclass
class WalletInput:
    api_key: str


@dataclass
class WalletOutput:
    api_key: str
    create_date_utc: datetime.datetime
    public_key: str
    btc_amount: float
    result_code: int = 0


@dataclass
class WalletInteractor:
    def add_wallet(
        btc_wallet_repository: IBTCWalletRepository, wallet: WalletInput
    ) -> WalletOutput:

        public_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        us = btc_wallet_repository.add_wallet(
            DbAddWalletIn(
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
