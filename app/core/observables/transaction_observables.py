import datetime
from dataclasses import dataclass, field
from typing import Protocol

from app.core import IBTCWalletRepository


@dataclass
class TransactionCreatedData:
    commission_btc: float
    create_date_utc: datetime.datetime


class ITransactionObserver(Protocol):
    def on_transaction_created(
        self, repo: IBTCWalletRepository, data: TransactionCreatedData
    ) -> None:
        pass


@dataclass
class TransactorObservable:
    observers: list[ITransactionObserver] = field(default_factory=list, init=False)

    def attach(self, observer: ITransactionObserver) -> None:
        self.observers.append(observer)

    def notify_transaction_created(
        self, repo: IBTCWalletRepository, data: TransactionCreatedData
    ) -> None:
        for observer in self.observers:
            observer.on_transaction_created(repo, data)
