import contextlib
import datetime
import os
from typing import Iterator

import pytest
from sqlalchemy import MetaData

from app.core import DbAddWalletIn, DbGetWalletIn, DbGetUserWalletCountIn, DbUpdateWalletBalanceIn, DbAddUserIn, DbAddTransactionIn, DbUserTransactionsOutput
from app.infra.data_repository import BTCWalletRepository
from app.utils import get_root_path
from app.utils.result_codes import ResultCode

connection_string = f"sqlite:///{get_root_path()}{os.sep}testing.sqlite"
repository = BTCWalletRepository(connection_string)


def truncate_db() -> None:
    metadata = MetaData(repository.engine)
    metadata.reflect()
    with contextlib.closing(repository.engine.connect()) as con:
        trans = con.begin()
        for table in reversed(metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


@pytest.fixture(autouse=True)
def run_around_tests() -> Iterator[
    None,
]:
    yield
    truncate_db()

def test_db_add_user() -> None:
    # create user
    name = "John"
    api_key = "John_api"
    create_date_utc = datetime.datetime.now()
    user = DbAddUserIn(
        name = name,
        api_key = api_key,
        create_date_utc = create_date_utc
    )

    # add user
    user_out = repository.add_user(user)
    assert user_out.name == name
    assert user_out.api_key == api_key
    assert user_out.create_date_utc == create_date_utc

def test_db_add_wallet() -> None:
    create_date_utc = datetime.datetime.now()
    api_key = "api"
    public_key = "pub"
    btc_amount = 2.0
    wallet = DbAddWalletIn(
        api_key=api_key,
        create_date_utc=create_date_utc,
        public_key=public_key,
        btc_amount=btc_amount,
    )
    created_wallet = repository.add_wallet(wallet)

    assert wallet.api_key == created_wallet.api_key
    assert wallet.btc_amount == created_wallet.btc_amount
    assert wallet.create_date_utc == created_wallet.create_date_utc
    assert wallet.public_key == created_wallet.public_key

def test_db_get_wallet() -> None:
    create_date_utc = datetime.datetime.now()
    api_key = "api"
    public_key = "pub"
    btc_amount = 2.0
    # add wallet
    wallet = DbAddWalletIn(
        api_key=api_key,
        create_date_utc=create_date_utc,
        public_key=public_key,
        btc_amount=btc_amount,
    )
    created_wallet = repository.add_wallet(wallet)

    # get created wallet
    getWalletDB = DbGetWalletIn(public_key = public_key)
    wallet_out = repository.fetch_wallet(getWalletDB)

    # assert fields
    assert wallet.api_key == wallet_out.api_key
    assert wallet.public_key == wallet_out.public_key
    assert wallet.btc_amount == wallet_out.btc_amount

def test_db_count_wallets_of_user() -> None:
    create_date_utc = datetime.datetime.now()
    api_key = "api"
    public_key = "pub"
    btc_amount = 2.0
    # add wallet
    wallet = DbAddWalletIn(
        api_key=api_key,
        create_date_utc=create_date_utc,
        public_key=public_key,
        btc_amount=btc_amount,
    )
    created_wallet = repository.add_wallet(wallet)

    # get wallet count
    coun_wallets_in = DbGetUserWalletCountIn(api_key = api_key)
    wallet_count_out = repository.count_wallets_of_user(coun_wallets_in)
    assert wallet_count_out.wallet_count == 1

def test_db_update_wallet_balance() -> None:
    create_date_utc = datetime.datetime.now()
    api_key = "api"
    public_key = "pub"
    btc_amount = 2.0
    updated_btc_amount = 5.3
    # add wallet
    wallet = DbAddWalletIn(
        api_key=api_key,
        create_date_utc=create_date_utc,
        public_key=public_key,
        btc_amount=btc_amount,
    )
    created_wallet = repository.add_wallet(wallet)

    # update wallet balance
    update_wallet_balance_in = DbUpdateWalletBalanceIn(public_key = public_key, amount = updated_btc_amount)
    wallet_update = repository.update_wallet_balance(update_wallet_balance_in)
    assert wallet_update.result_code == ResultCode.SUCCESS

    # get wallet and check corresponding balance
    getWalletDB = DbGetWalletIn(public_key = public_key)
    wallet_out = repository.fetch_wallet(getWalletDB)

    # assert fields
    assert wallet_out.btc_amount == updated_btc_amount + btc_amount

def test_db_add_transaction() -> None:
    # create transaction
    src_api_key = "src_api_key"
    src_public_key = "src_public_key"
    dst_public_key = "dst_public_key"
    btc_amount = 2.5
    commission = 0.3
    create_date_utc = datetime.datetime.now()
    transaction = DbAddTransactionIn(
        src_api_key = src_api_key,
        src_public_key = src_public_key,
        dst_public_key = dst_public_key,
        btc_amount = btc_amount,
        commission = commission,
        create_date_utc = create_date_utc,
    )

    # add transaction
    transaction_out = repository.add_transaction(transaction)
    assert transaction_out.src_api_key == src_api_key
    assert transaction_out.src_public_key == src_public_key
    assert transaction_out.dst_public_key == dst_public_key
    assert transaction_out.btc_amount == btc_amount
    assert transaction_out.commission == commission
    assert transaction_out.create_date_utc == create_date_utc

def test_db_fetch_user_transactions() -> None:
    # create transaction
    src_api_key = "src_api_key"
    src_public_key = "src_public_key"
    dst_public_key = "dst_public_key"
    btc_amount = 2.5
    commission = 0.3
    create_date_utc = datetime.datetime.now()
    transaction = DbAddTransactionIn(
        src_api_key = src_api_key,
        src_public_key = src_public_key,
        dst_public_key = dst_public_key,
        btc_amount = btc_amount,
        commission = commission,
        create_date_utc = create_date_utc,
    )

    # add transaction
    transaction_out = repository.add_transaction(transaction)

    # get user transactions
    user_transactions = repository.fetch_user_transactions(src_api_key)

    assert len(user_transactions.user_transactions) == 1
    assert user_transactions.user_transactions[0].src_api_key == src_api_key
    assert user_transactions.user_transactions[0].src_public_key == src_public_key
    assert user_transactions.user_transactions[0].dst_public_key == dst_public_key
    assert user_transactions.user_transactions[0].btc_amount == btc_amount
    assert user_transactions.user_transactions[0].commission == commission

def test_db_fetch_wallet_transactions() -> None:
    # create transaction
    src_api_key = "src_api_key"
    src_public_key = "src_public_key"
    dst_public_key = "dst_public_key"
    btc_amount = 2.5
    commission = 0.3
    create_date_utc = datetime.datetime.now()
    transaction = DbAddTransactionIn(
        src_api_key = src_api_key,
        src_public_key = src_public_key,
        dst_public_key = dst_public_key,
        btc_amount = btc_amount,
        commission = commission,
        create_date_utc = create_date_utc,
    )

    # add transaction
    transaction_out = repository.add_transaction(transaction)

    # fetch wallet transactions
    wallet_transactions = repository.fetch_wallet_transactions(src_public_key, src_api_key)

    assert len(wallet_transactions.wallet_transactions) == 1
    assert wallet_transactions.wallet_transactions[0].src_api_key == src_api_key
    assert wallet_transactions.wallet_transactions[0].src_public_key == src_public_key
    assert wallet_transactions.wallet_transactions[0].dst_public_key == dst_public_key
    assert wallet_transactions.wallet_transactions[0].btc_amount == btc_amount
    assert wallet_transactions.wallet_transactions[0].commission == commission
