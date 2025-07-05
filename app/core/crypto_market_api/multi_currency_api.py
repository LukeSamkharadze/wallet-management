import requests
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass
import time
from app.app_settings import AppSettings
from app.core.crypto_market_api import ICryptoMarketApi


class CryptoCurrency(Enum):
    """Supported cryptocurrency networks"""
    BTC = "bitcoin"
    ETH = "ethereum"
    BNB = "binancecoin"
    SOL = "solana"
    XRP = "ripple"
    TRX = "tron"
    DOGE = "dogecoin"
    ADA = "cardano"
    AVAX = "avalanche-2"
    MATIC = "matic-network"
    LINK = "chainlink"
    LTC = "litecoin"
    XLM = "stellar"
    XMR = "monero"
    DOT = "polkadot"
    
    @property
    def symbol(self) -> str:
        """Get the trading symbol"""
        return self.name
    
    @property
    def decimals(self) -> int:
        """Get the decimal places for each currency"""
        decimals_map = {
            "BTC": 8,
            "ETH": 18,
            "BNB": 18,
            "SOL": 9,
            "XRP": 6,
            "TRX": 6,
            "DOGE": 8,
            "ADA": 6,
            "AVAX": 18,
            "MATIC": 18,
            "LINK": 18,
            "LTC": 8,
            "XLM": 7,
            "XMR": 12,
            "DOT": 10,
        }
        return decimals_map.get(self.name, 8)
    
    @property
    def native_unit(self) -> str:
        """Get the smallest unit name (like satoshi for BTC)"""
        unit_map = {
            "BTC": "satoshi",
            "ETH": "wei",
            "BNB": "jager",
            "SOL": "lamport",
            "XRP": "drop",
            "TRX": "sun",
            "DOGE": "koinu",
            "ADA": "lovelace",
            "AVAX": "nAVAX",
            "MATIC": "wei",
            "LINK": "wei",
            "LTC": "litoshi",
            "XLM": "stroop",
            "XMR": "piconero",
            "DOT": "planck",
        }
        return unit_map.get(self.name, "unit")
    
    @classmethod
    def from_symbol(cls, symbol: str) -> Optional['CryptoCurrency']:
        """Get currency from symbol"""
        for currency in cls:
            if currency.name == symbol.upper():
                return currency
        return None


@dataclass
class CryptoPrice:
    """Represents cryptocurrency price data"""
    currency: CryptoCurrency
    usd_price: float
    btc_price: float
    market_cap: float
    volume_24h: float
    change_24h: float
    last_updated: int


class MultiCurrencyApi(ICryptoMarketApi):
    """Multi-currency API that supports multiple data sources"""
    
    def __init__(self):
        self._cache: Dict[str, CryptoPrice] = {}
        self._cache_ttl = 60  # Cache for 60 seconds
        self._last_fetch = 0
    
    def get_price_of_btc(self) -> float:
        """Legacy method for Bitcoin price"""
        price_data = self.get_crypto_price(CryptoCurrency.BTC)
        return price_data.usd_price if price_data else 0.0
    
    def get_crypto_price(self, currency: CryptoCurrency) -> Optional[CryptoPrice]:
        """Get price data for any supported cryptocurrency"""
        # Check cache first
        if self._should_use_cache():
            cached = self._cache.get(currency.value)
            if cached:
                return cached
        
        # Try multiple data sources
        price_data = self._fetch_from_coingecko(currency)
        if not price_data:
            price_data = self._fetch_from_blockchain_info(currency)
        if not price_data:
            price_data = self._fetch_from_binance(currency)
        
        if price_data:
            self._cache[currency.value] = price_data
            self._last_fetch = int(time.time())
        
        return price_data
    
    def get_crypto_price_in_usd(self, currency: CryptoCurrency, amount: float) -> float:
        """Convert cryptocurrency amount to USD"""
        price_data = self.get_crypto_price(currency)
        if price_data:
            return amount * price_data.usd_price
        return 0.0
    
    def get_all_prices(self) -> Dict[CryptoCurrency, CryptoPrice]:
        """Get prices for all supported cryptocurrencies"""
        prices = {}
        for currency in CryptoCurrency:
            price_data = self.get_crypto_price(currency)
            if price_data:
                prices[currency] = price_data
        return prices
    
    def _should_use_cache(self) -> bool:
        """Check if cache is still valid"""
        return int(time.time()) - self._last_fetch < self._cache_ttl
    
    def _fetch_from_coingecko(self, currency: CryptoCurrency) -> Optional[CryptoPrice]:
        """Fetch price from CoinGecko API"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": currency.value,
                "vs_currencies": "usd,btc",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if currency.value in data:
                    coin_data = data[currency.value]
                    return CryptoPrice(
                        currency=currency,
                        usd_price=coin_data.get("usd", 0),
                        btc_price=coin_data.get("btc", 0),
                        market_cap=coin_data.get("usd_market_cap", 0),
                        volume_24h=coin_data.get("usd_24h_vol", 0),
                        change_24h=coin_data.get("usd_24h_change", 0),
                        last_updated=coin_data.get("last_updated_at", int(time.time()))
                    )
        except Exception:
            pass
        return None
    
    def _fetch_from_blockchain_info(self, currency: CryptoCurrency) -> Optional[CryptoPrice]:
        """Fetch Bitcoin price from blockchain.info (Bitcoin only)"""
        if currency != CryptoCurrency.BTC:
            return None
        
        try:
            blockchain_config = AppSettings().get_config()["blockchain_api"]
            response = requests.get(
                blockchain_config["domain"] + blockchain_config["btc_market_data_endpoint"],
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                usd_data = data.get(blockchain_config["usd_symbol"], {})
                usd_price = float(usd_data.get(blockchain_config["price_field_name"], 0))
                
                return CryptoPrice(
                    currency=currency,
                    usd_price=usd_price,
                    btc_price=1.0,  # BTC to BTC is always 1
                    market_cap=0,  # Not provided by this API
                    volume_24h=0,
                    change_24h=0,
                    last_updated=int(time.time())
                )
        except Exception:
            pass
        return None
    
    def _fetch_from_binance(self, currency: CryptoCurrency) -> Optional[CryptoPrice]:
        """Fetch price from Binance API"""
        try:
            # Map currency to Binance symbols
            symbol_map = {
                CryptoCurrency.BTC: "BTCUSDT",
                CryptoCurrency.ETH: "ETHUSDT",
                CryptoCurrency.BNB: "BNBUSDT",
                CryptoCurrency.SOL: "SOLUSDT",
                CryptoCurrency.XRP: "XRPUSDT",
                CryptoCurrency.TRX: "TRXUSDT",
                CryptoCurrency.DOGE: "DOGEUSDT",
                CryptoCurrency.ADA: "ADAUSDT",
                CryptoCurrency.AVAX: "AVAXUSDT",
                CryptoCurrency.MATIC: "MATICUSDT",
                CryptoCurrency.LINK: "LINKUSDT",
                CryptoCurrency.LTC: "LTCUSDT",
                CryptoCurrency.XLM: "XLMUSDT",
                CryptoCurrency.DOT: "DOTUSDT",
            }
            
            symbol = symbol_map.get(currency)
            if not symbol:
                return None
            
            # Get 24hr ticker data
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                usd_price = float(data.get("lastPrice", 0))
                
                # Get BTC price if not Bitcoin
                btc_price = 1.0 if currency == CryptoCurrency.BTC else 0
                if currency != CryptoCurrency.BTC:
                    btc_response = requests.get(
                        url, 
                        params={"symbol": f"{currency.name}BTC"}, 
                        timeout=5
                    )
                    if btc_response.status_code == 200:
                        btc_data = btc_response.json()
                        btc_price = float(btc_data.get("lastPrice", 0))
                
                return CryptoPrice(
                    currency=currency,
                    usd_price=usd_price,
                    btc_price=btc_price,
                    market_cap=0,  # Not provided by ticker API
                    volume_24h=float(data.get("volume", 0)) * usd_price,
                    change_24h=float(data.get("priceChangePercent", 0)),
                    last_updated=int(time.time())
                )
        except Exception:
            pass
        return None