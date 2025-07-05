from typing import Protocol, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .multi_currency_api import CryptoCurrency, CryptoPrice


class ICryptoMarketApi(Protocol):
    def get_price_of_btc(self) -> float:
        """Legacy method for Bitcoin price"""
        ...
    
    def get_crypto_price(self, currency: 'CryptoCurrency') -> Optional['CryptoPrice']:
        """Get price data for any supported cryptocurrency"""
        ...
    
    def get_crypto_price_in_usd(self, currency: 'CryptoCurrency', amount: float) -> float:
        """Convert cryptocurrency amount to USD"""
        ...
    
    def get_all_prices(self) -> Dict['CryptoCurrency', 'CryptoPrice']:
        """Get prices for all supported cryptocurrencies"""
        ...


# Export the multi-currency classes for easier imports
__all__ = ['ICryptoMarketApi']

# Import the concrete implementations when not type checking
if not TYPE_CHECKING:
    from .multi_currency_api import CryptoCurrency, CryptoPrice, MultiCurrencyApi
    __all__.extend(['CryptoCurrency', 'CryptoPrice', 'MultiCurrencyApi'])
