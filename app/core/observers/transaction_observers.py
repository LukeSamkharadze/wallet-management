from app.core import DbUpdateCommissionStatsIn, IBTCWalletRepository
from app.core.observables.transaction_observables import (
    ITransactionObserver,
    TransactionCreatedData,
)


class SystemTransactionObserver(ITransactionObserver):
    def on_transaction_created(
        self, repo: IBTCWalletRepository, data: TransactionCreatedData
    ) -> None:
        repo.update_commission_stats(
            DbUpdateCommissionStatsIn(commission_amount_btc=data.commission_btc)
        )
