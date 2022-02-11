from typing import Protocol


class ICryptoMarketApi(Protocol):
    def get_price_of_btc(self) -> float:
        pass
