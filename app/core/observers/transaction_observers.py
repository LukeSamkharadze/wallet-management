from app.core import DbUpdateCommissionStatsIn, IWalletRepository
from app.core.observables.transaction_observables import (
    ITransactionObserver,
    TransactionCreatedData,
)


class SystemTransactionObserver(ITransactionObserver):
    def on_transaction_created(
        self, repo: IWalletRepository, data: TransactionCreatedData
    ) -> None:
        repo.update_commission_stats(
            DbUpdateCommissionStatsIn(
                commission_amount=data.commission,
                currency=data.currency,
                create_date_utc=data.create_date_utc,
            )
        )
