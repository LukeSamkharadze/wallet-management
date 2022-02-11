import datetime
import uuid
from dataclasses import dataclass

from app.core import BaseInteractorOutput, DbAddUserIn, IBTCWalletRepository


@dataclass
class UserInput:
    name: str


@dataclass
class UserOutput(BaseInteractorOutput):
    name: str
    api_key: str
    create_date_utc: datetime.datetime


@dataclass
class UserInteractor:
    @staticmethod
    def add_user(
        btc_wallet_repository: IBTCWalletRepository, user: UserInput
    ) -> UserOutput:

        api_key = uuid.uuid4().hex
        create_date_utc = datetime.datetime.now()
        us = btc_wallet_repository.add_user(
            DbAddUserIn(
                name=user.name, api_key=api_key, create_date_utc=create_date_utc
            )
        )

        return UserOutput(
            name=us.name,
            api_key=us.api_key,
            create_date_utc=us.create_date_utc,
            result_code=us.result_code,
        )
