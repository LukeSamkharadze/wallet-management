import requests

from app.app_settings import AppSettings
from app.crypto_market_api import ICryptoMarketApi


class BlockchainApi(ICryptoMarketApi):
    def get_price_of_btc(self) -> float:
        blockchain_config = AppSettings().get_config()["blockchain_api"]
        x = requests.get(
            blockchain_config["domain"] + blockchain_config["btc_market_data_endpoint"]
        )
        return float(
            x.json()[blockchain_config["usd_symbol"]][
                blockchain_config["price_field_name"]
            ]
        )
