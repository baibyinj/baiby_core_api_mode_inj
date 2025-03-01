from pathlib import Path
import json
import os
import dotenv
from multiversx_sdk import Account, DevnetEntrypoint, Transaction, Address, ProxyNetworkProvider
from multiversx_sdk.wallet import UserSigner

dotenv.load_dotenv()

# CONFIGURACIÓN
PROVIDER_URL = "https://testnet-gateway.multiversx.com"  # Cambiado a testnet
RECEIVER_ADDRESS = "erd1md66ra4tfmpack774z6yfytwwn68azr43utsddv09v785wtqa9wq44kl46"  # Dirección del destinatario
AMOUNT = 0.001  # Cantidad de EGLD a enviar
GAS_LIMIT = 50000  # Límite de gas para una transferencia simple

# Inicializar conexión con MultiversX
provider = ProxyNetworkProvider(PROVIDER_URL)

def create_account():
    entrypoint = DevnetEntrypoint()
    
    # Cargar la cuenta desde el archivo keystore JSON
    account = Account.new_from_keystore(
        file_path=Path("user_agent/wallet.json"),
        password=os.getenv("WALLET_PASSWORD")
    )
    
    # Obtener y establecer el nonce de la cuenta
    account_on_network = provider.get_account(account.address)
    account.nonce = account_on_network.nonce
    
    return account

if __name__ == "__main__":
    # Cargar cuenta
    account = create_account()
    
    # Crear transacción
    transaction = Transaction(
        nonce=account.nonce,
        sender=account.address,
        receiver=Address.new_from_bech32(RECEIVER_ADDRESS),
        value=int(AMOUNT * 10**18),  # Convertir EGLD a su denominación más pequeña
        gas_limit=GAS_LIMIT,
        chain_id="T",  # T para testnet
        version=1
    )
    
    # Firmar transacción
    transaction.signature = account.sign_transaction(transaction)
    
    # Enviar transacción
    tx_hash = provider.send_transaction(transaction)
    
    print(f"Transacción enviada. Hash: {tx_hash}")
