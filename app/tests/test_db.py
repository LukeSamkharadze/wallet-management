import contextlib
import datetime
import os
from typing import Iterator

import pytest
from sqlalchemy import MetaData

from app.core import DbAddWalletIn
from app.infra.data_repository import BTCWalletRepository
from app.utils import get_root_path

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