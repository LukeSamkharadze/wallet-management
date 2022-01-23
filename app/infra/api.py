from fastapi import APIRouter

wallet_api = APIRouter()


@wallet_api.get("/wallets/{address}")
def fetch_wallet(address: str) -> None:
    pass
