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

- **Balance Monitor:** Detects potential wallet draining attempts
  - Tracks transactions using >90% of wallet balance
  - Real-time balance checking
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





































# 3. bAIby_core bAIby_agent sentinel_bots


## Setup Instructions

### Environment Configuration

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
WS_BOT_URL=ws://localhost:8000/ws/bot
TX_AGENT_URL=http://localhost:8001/tx_agent
```

### Running the System

```
# Start main application bAIby_core
uvicorn app.main:app --reload

# Launch bAIby_agent
uvicorn baiby_agent.txagent:app --port 8001

# Start injective monitoring bot
python test_bot_new_address_inj.py
```

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


