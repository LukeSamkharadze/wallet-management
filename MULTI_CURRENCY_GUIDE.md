# Multi-Currency Wallet API Guide

## Overview

This wallet API now supports multiple cryptocurrency networks, allowing users to create wallets, make transactions, and track balances across 15 different cryptocurrencies.

## Supported Cryptocurrencies

The following cryptocurrencies are now supported:

| Symbol | Name | Decimal Places | Native Unit |
|--------|------|----------------|-------------|
| BTC | Bitcoin | 8 | satoshi |
| ETH | Ethereum | 18 | wei |
| BNB | BNB | 18 | jager |
| SOL | Solana | 9 | lamport |
| XRP | XRP | 6 | drop |
| TRX | TRON | 6 | sun |
| DOGE | Dogecoin | 8 | koinu |
| ADA | Cardano | 6 | lovelace |
| AVAX | Avalanche | 18 | nAVAX |
| MATIC | Polygon | 18 | wei |
| LINK | Chainlink | 18 | wei |
| LTC | Litecoin | 8 | litoshi |
| XLM | Stellar | 7 | stroop |
| XMR | Monero | 12 | piconero |
| DOT | Polkadot | 10 | planck |

## API Changes

### Creating a Wallet

**Endpoint:** `POST /wallets`

**Request Body:**
```json
{
  "api_key": "your_api_key",
  "currency": "BTC"  // New required field
}
```

**Response:**
```json
{
  "api_key": "your_api_key",
  "create_date_utc": "2024-01-01T00:00:00",
  "public_key": "wallet_address",
  "amount": 1.0,  // Changed from btc_amount
  "currency": "BTC",  // New field
  "usd_balance": 42000.0,  // New field showing USD value
  "result_code": "SUCCESS"
}
```

### Fetching Wallet Information

**Endpoint:** `GET /wallets/{address}`

**Response:**
```json
{
  "address": "wallet_address",
  "balance": 1.0,  // Changed from btc_balance
  "currency": "BTC",  // New field
  "usd_balance": 42000.0,
  "result_code": "SUCCESS"
}
```

### Creating Transactions

**Endpoint:** `POST /transactions`

**Request Body:**
```json
{
  "api_key": "your_api_key",
  "source_address": "source_wallet",
  "dest_address": "destination_wallet",
  "amount": 0.5  // Changed from btc_amount
}
```

**Note:** The currency is automatically determined from the source wallet. Both wallets must use the same currency.

**Response:**
```json
{
  "src_api_key": "your_api_key",
  "src_public_key": "source_wallet",
  "dst_public_key": "destination_wallet",
  "amount": 0.5,  // Changed from btc_amount
  "dest_amount": 0.4925,  // Changed from dest_btc_amount
  "currency": "BTC",  // New field
  "commission": 0.0075,
  "create_date_utc": "2024-01-01T00:00:00",
  "result_code": "SUCCESS"
}
```

### Fetching Statistics

**Endpoint:** `GET /statistics?currency=BTC`

**Query Parameters:**
- `currency` (optional): Filter statistics by currency

**Response:**
```json
{
  "commissions_sum": 10.5,  // Changed from commissions_sum_btc
  "currency": "BTC",  // New field
  "transactions_total_amount": 150,
  "result_code": "SUCCESS"
}
```

## Price Data Sources

The API uses multiple price data sources for reliability:
1. **CoinGecko API** (Primary)
2. **Binance API** (Secondary)
3. **Blockchain.info** (Bitcoin only, Tertiary)

If one source fails, the system automatically falls back to the next available source.

## Important Notes

1. **Initial Deposits**: When creating a new wallet, it receives an initial deposit equivalent to 1 BTC in the chosen currency.

2. **Wallet Limits**: Users can create up to 3 wallets per currency (configurable in settings).

3. **Transaction Rules**:
   - Transactions can only occur between wallets of the same currency
   - Cross-currency transactions are not supported (use an exchange for that)
   - Commission is 1.5% for external transfers, 0% for transfers between your own wallets

4. **Price Caching**: Price data is cached for 60 seconds to reduce API calls and improve performance.

## Error Codes

New error codes related to multi-currency support:
- `INVALID_CURRENCY (34)`: The specified cryptocurrency is not supported
- `CURRENCY_MISMATCH (35)`: Attempting to transfer between wallets with different currencies

## Migration Notes

If you're upgrading from the Bitcoin-only version:
1. The database schema has changed - old wallets will need migration
2. All amount fields have been renamed (btc_amount → amount)
3. The `currency` field is now required when creating wallets
4. API responses include currency information

## Example Usage

### Creating an Ethereum Wallet
```bash
curl -X POST http://localhost:8000/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "currency": "ETH"
  }'
```

### Creating a Solana Wallet
```bash
curl -X POST http://localhost:8000/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "currency": "SOL"
  }'
```

### Transferring DOGE between wallets
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your_api_key",
    "source_address": "doge_wallet_1",
    "dest_address": "doge_wallet_2",
    "amount": 100.0
  }'
```