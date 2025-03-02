from pathlib import Path
import json
import os
import dotenv
import httpx
from multiversx_sdk import Account, DevnetEntrypoint, Transaction, Address, ProxyNetworkProvider
from multiversx_sdk.wallet import UserSigner

dotenv.load_dotenv()

# CONFIGURACIÓN
PROVIDER_URL = "https://testnet-gateway.multiversx.com"
API_URL = "http://localhost:8000/agent/transaction/"
RECEIVER_ADDRESS = "erd1md66ra4tfmpack774z6yfytwwn68azr43utsddv09v785wtqa9wq44kl46"
#AMOUNT = 0.001
AMOUNT = 4.99895
GAS_LIMIT = 50000

provider = ProxyNetworkProvider(PROVIDER_URL)

def create_account():
    entrypoint = DevnetEntrypoint()
    account = Account.new_from_keystore(
        file_path=Path("user_agent/wallet.json"),
        password=os.getenv("WALLET_PASSWORD")
    )
    account_on_network = provider.get_account(account.address)
    account.nonce = account_on_network.nonce
    return account

async def send_transaction_to_api(transaction):
    # Preparar los datos de la transacción en el formato esperado
    tx_data = {
        "safeAddress": str(transaction.sender),
        "erc20TokenAddress": "EGLD",  # En este caso es EGLD nativo
        #"reason": "send some EGLD, because a user requested",  
        "reason": "need to transfer all EGLD, to start a new wallet",
        "transactions": [{
            "to": str(transaction.receiver),
            "data": transaction.data.decode() if transaction.data else "",
            "value": str(transaction.value)
        }]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=tx_data)
        return response.json()

if __name__ == "__main__":
    import asyncio
    
    # Cargar cuenta
    account = create_account()
    
    # Crear transacción
    transaction = Transaction(
        nonce=account.nonce,
        sender=account.address,
        receiver=Address.new_from_bech32(RECEIVER_ADDRESS),
        value=int(AMOUNT * 10**18),
        gas_limit=GAS_LIMIT,
        chain_id="T",
        version=1
    )
    
    # Firmar transacción
    transaction.signature = account.sign_transaction(transaction)
    
    # Enviar a nuestra API primero
    result = asyncio.run(send_transaction_to_api(transaction))
    print(f"API Response: {result}")
    
    # Si todo está bien, enviar a la blockchain
    #tx_hash = provider.send_transaction(transaction)
    #print(f"Transacción enviada. Hash: {tx_hash}")
