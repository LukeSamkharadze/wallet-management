from app.core.crypto_market_api.blockchain_api import BlockchainApi
from app.core.facade import BTCWalletCore
from app.infra.api import CreateWalletIn, RegisterUserIn, create_wallet, register_user
from app.infra.in_memory_data_repository import InMemoryBtcWalletRepository
from app.utils.result_codes import ResultCode


def test_api_should_register_user() -> None:
    repository = BTCWalletCore.create(
        btc_wallet_repository=InMemoryBtcWalletRepository(),
        crypto_market_api=BlockchainApi(),
    )

    user = RegisterUserIn()
    user.name = "dato"
    createdUser = register_user(user, repository)

    assert createdUser.name == user.name
    assert createdUser.result_code == ResultCode.SUCCESS


def test_api_should_create_wallet() -> None:
    repository = BTCWalletCore.create(
        btc_wallet_repository=InMemoryBtcWalletRepository(),
        crypto_market_api=BlockchainApi(),
    )
    user = RegisterUserIn()
    user.name = "dato"
    createdUser = register_user(user, repository)

    assert createdUser.name == user.name
    assert createdUser.result_code == ResultCode.SUCCESS

    wallet = CreateWalletIn()
    wallet.api_key = createdUser.api_key
    createdWallet = create_wallet(wallet, repository)

    assert createdWallet.api_key == wallet.api_key
    assert createdWallet.result_code == ResultCode.SUCCESS


# TODO: Test max_wallet_per_user here
def test_api_should_limit_wallets_per_user() -> None:
    pass


# TODO: Test new_wallet_deposit_btc here
def test_api_should_set_wallet_balance() -> None:
    pass


def test_api_should_get_wallet_by_address() -> None:
    pass


# TODO: Test that I can't access other's wallets
def test_api_should_limit_wallet_access() -> None:
    pass


def test_api_should_make_transaction() -> None:
    pass


def test_api_should_update_transaction_wallet_balances() -> None:
    pass


# TODO: Test that I can't make transaction with other users' wallets
def test_api_should_limit_transaction_creation_access() -> None:
    pass


# TODO: Test commission_fraction here
def test_api_should_tax_foreign_transactions() -> None:
    pass


# TODO: Test domestic_transfer_commission_fraction here
def test_api_should_tax_domestic_transactions() -> None:
    pass


def test_api_should_get_user_transactions() -> None:
    pass


# TODO: Test that I can't see other users' transactions
def test_api_should_limit_user_transaction_access() -> None:
    pass


def test_api_should_get_wallet_transactions() -> None:
    pass


# TODO: Test that I can't see other users' wallet transactions
def test_api_should_limit_wallet_transaction_access() -> None:
    pass


def test_api_should_get_admin_statistics() -> None:
    pass


# TODO: Test that I can't see statistics, unless i'm an admin
def test_api_should_limit_admin_statistics_access() -> None:
    pass
