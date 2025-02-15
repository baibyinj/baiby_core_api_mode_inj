# Crypto Transaction Risk Analysis System

## Overview
This system monitors cryptocurrency transactions in real-time and analyzes different risk factors, including:

- Token volatility
- Malicious addresses 
- Suspicious swap patterns

<img width="891" alt="Image" src="https://github.com/user-attachments/assets/61cb7318-b533-46f4-93ee-95b5fbe43b70" />

<img width="891" alt="Image" src="https://github.com/user-attachments/assets/62ce534d-6be0-4633-96ec-166ed01888f0" />

## Main Components

### Bots
The system includes several specialized bots:

- **Risk Bot**: Analyzes token volatility and market metrics
- **Malicious Address Bot**: Verifies addresses against GoPlus API
- **Swap Monitor Bot**: Monitors and decodes swap transactions and analyze the risk of the token

### Key Features

#### Risk Analysis
- Daily and annual volatility calculation
- Risk classification in three levels: High, Medium and Low
- Market cap and volume monitoring

#### Malicious Address Detection
- GoPlus Security API integration
- Multiple risk categories verification
- Real-time alerts

#### Transaction Decoding
- Support for swap transactions
- Calldata decoding
- Address and parameter extraction

## Setup

### Requirements
- Python 3.8+
- WebSocket Server
- APIs:
  - CoinGecko
  - GoPlus Security



## How to Test de app

### 1. Integration with SafeWallet Module
First, ensure you have the SafeWallet module properly configured for Arbitrum network:
### 2. test the Specialized Bots
#### Risk Analysis Bot
Monitors token volatility and market risk:
This bot will:
- Decode swap transactions
- Analyze token market data
- Alert on high volatility tokens

USE: send a swap transaction on uniswap v3 on arbitrum network


#### Malicious Address Detection
Checks for suspicious addresses:
Features:
- GoPlus Security API integration
- Real-time address verification
- Scam detection alerts

USE: send a transaction to a malicious address

#### Balance Theft Protection
Monitors for suspicious balance drains:
Capabilities:
- Monitors native token balance
- Detects full balance transfers
- Alerts on suspicious patterns

USE: send a transaction for native token on arbitrum network with 99% of balance
