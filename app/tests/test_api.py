import json
from typing import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.app_settings import AppSettings
from app.core.crypto_market_api.blockchain_api import BlockchainApi
from app.core.facade import BTCWalletCore
from app.infra.api import (
    CreateTransactionIn,
    CreateWalletIn,
    RegisterUserIn,
    get_btc_wallet_core,
    wallet_api,
)
from app.infra.in_memory_data_repository import InMemoryBtcWalletRepository
from app.utils.result_codes import ResultCode

app = FastAPI()

app.include_router(wallet_api)

inMemoryBtcWalletRepository = InMemoryBtcWalletRepository()

core = BTCWalletCore.create(
    btc_wallet_repository=inMemoryBtcWalletRepository,
    crypto_market_api=BlockchainApi(),
)


def override_get_btc_wallet_core() -> BTCWalletCore:
    return core


app.dependency_overrides[get_btc_wallet_core] = override_get_btc_wallet_core

client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests() -> Iterator[None]:
    yield
    inMemoryBtcWalletRepository.truncate()


def test_api_should_register_user() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    assert created_user["name"] == user.name
    assert (
        ResultCode.get_enum_from_code(created_user["result_code"][0])
        == ResultCode.SUCCESS
    )


def test_api_should_create_wallet() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)

    assert created_wallet["api_key"] == wallet.api_key
    assert created_wallet["btc_amount"] == float(
        AppSettings().get_config()["wallet"]["new_wallet_deposit_btc"]
    )
    assert (
        ResultCode.get_enum_from_code(created_wallet["result_code"][0])
        == ResultCode.SUCCESS
    )


def test_api_should_limit_wallets_per_user() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    for i in range(int(AppSettings().get_config()["wallet"]["max_wallet_per_user"])):
        wallet = CreateWalletIn()
        wallet.api_key = created_user["api_key"]
        created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)

    assert (
        ResultCode.get_enum_from_code(created_wallet["result_code"][0])
        == ResultCode.WALLET_LIMIT_PER_USER_REACHED
    )


def test_api_should_get_wallet_by_address() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)

    fetched_wallet = json.loads(
        client.get(
            f"/wallets/{created_wallet['public_key']}",
            headers={"api_key": wallet.api_key},
        ).content
    )

    assert fetched_wallet["address"] == created_wallet["public_key"]
    assert fetched_wallet["btc_balance"] == created_wallet["btc_amount"]
    assert fetched_wallet["usd_balance"]


def test_api_should_make_transaction() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)

    transaction = CreateTransactionIn()
    transaction.api_key = wallet.api_key
    transaction.source_address = created_wallet["public_key"]
    transaction.dest_address = created_wallet["public_key"]
    transaction.btc_amount = 1

    created_transaction = json.loads(
        client.post("/transactions", transaction.toJSON()).content
    )

    assert created_transaction["src_api_key"] == transaction.api_key
    assert created_transaction["src_public_key"] == transaction.source_address
    assert created_transaction["dst_public_key"] == transaction.dest_address
    assert created_transaction["btc_amount"] == transaction.btc_amount


def test_api_should_update_transaction_wallet_balances() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)
    created_wallet_2 = json.loads(client.post("/wallets", wallet.toJSON()).content)

    transaction = CreateTransactionIn()
    transaction.api_key = wallet.api_key
    transaction.source_address = created_wallet["public_key"]
    transaction.dest_address = created_wallet_2["public_key"]
    transaction.btc_amount = 1

    created_transaction = json.loads(
        client.post("/transactions", transaction.toJSON()).content
    )

    fetched_wallet = json.loads(
        client.get(
            f"/wallets/{created_wallet['public_key']}",
            headers={"api_key": wallet.api_key},
        ).content
    )
    fetched_wallet_2 = json.loads(
        client.get(
            f"/wallets/{created_wallet_2['public_key']}",
            headers={"api_key": wallet.api_key},
        ).content
    )

    assert fetched_wallet["btc_balance"] == 0
    assert fetched_wallet_2["btc_balance"] == 1.985


def test_api_should_tax_foreign_transactions() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    created_user = json.loads(client.post("/users", user.toJSON()).content)
    created_user_2 = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = created_user["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)
    wallet = CreateWalletIn()
    wallet.api_key = created_user_2["api_key"]
    created_wallet_2 = json.loads(client.post("/wallets", wallet.toJSON()).content)

    transaction = CreateTransactionIn()
    transaction.api_key = wallet.api_key
    transaction.source_address = created_wallet["public_key"]
    transaction.dest_address = created_wallet_2["public_key"]
    transaction.btc_amount = 100

    created_transaction = json.loads(
        client.post("/transactions", transaction.toJSON()).content
    )

    print(created_transaction["commission"])

    # fetched_wallet = json.loads(
    #     client.get(
    #         f"/wallets/{created_wallet['public_key']}",
    #         headers={"api_key": wallet.api_key},
    #     ).content
    # )
    # fetched_wallet_2 = json.loads(
    #     client.get(
    #         f"/wallets/{created_wallet_2['public_key']}",
    #         headers={"api_key": wallet.api_key},
    #     ).content
    # )

    # assert fetched_wallet["btc_balance"] == 1.0
    # assert fetched_wallet_2["btc_balance"] == 1.0


def test_api_should_tax_domestic_transactions() -> None:
    user = RegisterUserIn()
    user.name = "dato"
    createdUser = json.loads(client.post("/users", user.toJSON()).content)

    wallet = CreateWalletIn()
    wallet.api_key = createdUser["api_key"]
    created_wallet = json.loads(client.post("/wallets", wallet.toJSON()).content)
    created_wallet_2 = json.loads(client.post("/wallets", wallet.toJSON()).content)

    transaction = CreateTransactionIn()
    transaction.api_key = wallet.api_key
    transaction.source_address = created_wallet["public_key"]
    transaction.dest_address = created_wallet_2["public_key"]
    transaction.btc_amount = 100

    created_transaction = json.loads(
        client.post("/transactions", transaction.toJSON()).content
    )

    print(created_transaction["commission"])


def test_api_should_get_user_transactions() -> None:
    pass


def test_api_should_get_wallet_transactions() -> None:
    pass


def test_api_should_get_admin_statistics() -> None:
    pass


# TODO: Test that I can't see other users' transactions
# def test_api_should_limit_user_transaction_access() -> None:
#     pass


# TODO: Test that I can't see other users' wallet transactions
# def test_api_should_limit_wallet_transaction_access() -> None:
#     pass


# TODO: Test that I can't access other's wallets
# def test_api_should_limit_wallet_access() -> None:
#     pass

# TODO: Test that I can't make transaction with other users' wallets
# def test_api_should_limit_transaction_creation_access() -> None:
#     pass

# TODO: Test that I can't see statistics, unless i'm an admin
# def test_api_should_limit_admin_statistics_access() -> None:
#     pass
