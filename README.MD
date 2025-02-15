# Crypto Transaction Risk Analysis System

#test Features you can test in the live DEMO

-USE: send a swap transaction on uniswap v3 on arbitrum network

-USE: send a transaction to a malicious address

-USE: send a transaction for native token on arbitrum network with 99% of balance

## Overview
This system monitors cryptocurrency transactions in real-time and analyzes different risk factors, including:

- Token volatility
- Malicious addresses 
- Suspicious swap patterns

# Bot System and Agent Alerts Architecture

## Overview
The system uses a WebSocket-based architecture to monitor transactions and communicate alerts between bots and agents.

## System Architecture

<img width="811" alt="Image" src="https://github.com/user-attachments/assets/6e3f16d7-e2ee-4c33-a8f6-3d22e79026ce" />

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
