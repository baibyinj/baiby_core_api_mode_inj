# bAIbysitter - Intelligent Transaction Guardian

bAIbysitter is a decentralized transaction monitoring system that uses AI to protect agents and humans from potentially harmful transactions or money losses. The system comprises three key components working in harmony to ensure transaction safety.

## Key Components

Architecture

<img width="907" alt="Image" src="https://github.com/user-attachments/assets/c7856046-75fc-44eb-bcd7-e10256501659" />

### 1. bAIby Agent (AI Decision Maker)

- Powered by GPT-4 for intelligent transaction analysis
- Processes warnings from monitoring bots
- Makes final approval/rejection decisions
- Stores transaction history in Supabase
- Provides detailed reasoning for each decision

### 2. Monitoring Bots

Currently focused on injective blockchain monitoring:

- **new Wallet transaction:** Detects transactions to a neww wallet
  - new wallet
  - first transaction to this wallet
  - Immediate warning generation for suspicious patterns

### 3. Main Application

Orchestrates the entire transaction flow:

- Receives incoming transactions
- Manages WebSocket connections with monitoring bots
- Coordinates communication between components
- Handles timeouts and retries
- Returns final decisions to users


# Injective iAgent - bAIbysitter Security plugin integration

## Description

bAIbysitter is a new security feature integrated into iAgent that uses AI to validate transactions by comparing them with their intended purpose and protect users from potentially risky operations.

## Main Components

### 1. TransactionBabysitter

```python
/iAgent-naster/injective_functions/baibysitter/baibysitter.py
class TransactionBabysitter(InjectiveBase):
    def __init__(self, chain_client, api_url: str) -> None:
        super().__init__(chain_client)
        self.api_url = api_url

    async def safe_transfer(self, amount: Decimal, denom: str, to_address: str, chat_history: list) -> Dict:
        # AI-based transaction validation
        validation = await self.validate_with_api(
            tx_payload=str(msg),
            chat_history=chat_history,
            sender=self.chain_client.address.to_acc_bech32(),
            recipient=to_address,
            amount=amount,
            denom=denom
        )

        if validation.get("status") == "success" and "APPROVED" in validation.get("message", ""):
            return await self.chain_client.build_and_broadcast_tx(msg)
        return {"success": False, "error": f"Transaction rejected: {validation.get('message')}"}
```

### 2. Integration with InjectiveBank

```python
/iAgent-naster/injective_functions/bank/__init__.py
class InjectiveBank(InjectiveBase):
    def __init__(self, chain_client, api_url: str = None) -> None:
        super().__init__(chain_client)
        self.babysitter = TransactionBabysitter(chain_client, api_url) if api_url else None

    async def transfer_funds(self, amount: Decimal, denom: str, to_address: str, chat_history: list = None) -> Dict:
        if self.babysitter and chat_history is not None:
            return await self.babysitter.safe_transfer(
                amount=amount,
                denom=denom,
                to_address=to_address,
                chat_history=chat_history
            )
```

## Quick Setup

### Environment Variables

```bash
TX_AGENT_URL=http://localhost:8001/  # Validation service URL
```

## Basic Usage

```python
# Create client with babysitter
clients = await InjectiveClientFactory.create_all(
    private_key=private_key,
    network_type="testnet",
    api_url="http://localhost:8001/"
)

# Perform secure transfer
result = await clients["bank"].transfer_funds(
    amount=Decimal("0.1"),
    denom="INJ",
    to_address="inj1...",
    chat_history=chat_history
)
```

## Key Features

- **Automatic Validation:** Analyzes each transaction before execution.
- **Smart Context:** Uses chat history to make decisions.
- **Transparent Integration:** Automatically activates when configured.
- **Safe Mode:** Rejects suspicious transactions.

## Operation Flow

1. The user requests the agent to make a transaction.
2. bAIbysitter analyzes the transaction along with the transaction intent based on chat history.
3. If approved → Executes transfer.
4. If rejected → Returns an explanatory message.

## Considerations

- Only active when `api_url` and `chat_history` are provided.
- Currently works exclusively for banking transactions.
- Adds an extra layer of security without complicating usage.

## Future Improvements

- Support for more transaction types.
- Customizable validation rules.
- Integration with other iAgent modules.



### Running the System

```
# Start main application bAIby_core
uvicorn app.main:app --reload

# Launch bAIby_agent
uvicorn baiby_agent.txagent:app --port 8001

# Start injective monitoring bot
python test_bot_new_address_inj.py
```





# Bot Detection of First Transaction to a Wallet

/bots/test_bot_new_address_inj.py

### `fetch_account_txs`
- Queries the transaction history of an address
- Determines if the account has previous transactions

### `fetch_bank_balances`
- Checks the current balance of the address
- Determines if the account has funds




# bAIby_core API

### Environment Configuration



```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
WS_BOT_URL=ws://localhost:8000/ws/bot
TX_AGENT_URL=http://localhost:8001/tx_agent
```

## 1. Transaction Reception
```python
@router.post("/agent/transaction/", response_model=TransactionResponse)
async def process_agent_transaction(transaction: TransactionRequest):
    # Serialize and generate hash
    tx_data = serialize_transaction(transaction)
    transaction_hash = hashlib.sha256(
        json.dumps(tx_data, sort_keys=True).encode()
    ).hexdigest()
    
    # Prepare message for bots
    tx_message = {
        "type": "transaction",
        "data": {
            "transactions": tx_data["transactions"],
            "hash": transaction_hash,
            "safewallet": tx_data["safeAddress"]
        }
    }
```

## 2. Broadcast to Bots and Await Response
```python
await ws_manager.broadcast(tx_message)
tx_agent_response = await process_transaction_with_timeout(
    tx_data,
    transaction_hash
)
```

## 3. Final Decision and Response
```python
return TransactionResponse(
    status="success",
    message=f"Transaction {tx_agent_response.get('approval_status', 'PENDING')} - {tx_agent_response.get('llm_response', '')}",
    transaction_hash=transaction_hash,
    approval_status=tx_agent_response.get('approval_status', 'PENDING')
)
```

## Key Components

### WebSocket Manager
- Manages connections with bots
- Distributes transaction information
- Collects alerts and warnings

### Transaction Processing
- 5-second timeout for bot responses
- Parallel analysis
- Logs transactions in Supabase

### Client Response
- Transaction status
- Detailed reasoning
- Hash for tracking


## Technical Details

### Stack

- Backend: FastAPI
- AI: OpenAI GPT-4
- Database: Supabase
- Blockchain: injective
- Real-time: WebSockets
- HTTP Client: HTTPX

### Security Features

- Real-time transaction monitoring
- AI-powered risk assessment
- Comprehensive error logging
- Transaction audit trail
- Multiple retry mechanisms
- Timeout handling

## Future Development

- Additional monitoring bots
- Enhanced AI capabilities
- Multi-chain support
- Advanced risk scoring
- User preferences


