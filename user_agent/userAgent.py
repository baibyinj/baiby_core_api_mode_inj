from multiversx_sdk import ProxyNetworkProvider
from multiversx_sdk.wallet import Account, UserSigner
from multiversx_sdk.transaction import Transaction, TransactionPayload
from multiversx_sdk.utils import Bunch, TokenPayment
from multiversx_sdk.contracts import SmartContract
import json

# CONFIGURACIÓN
PROVIDER_URL = "https://gateway.multiversx.com"
PRIVATE_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # Clave privada en formato hexadecimal
ADDRESS = "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6g6t7"  # Dirección de tu billetera
TOKEN_IN = "EGLD"  # Token que envías (por ejemplo, EGLD)
TOKEN_OUT = "USDC-123456"  # Token que quieres recibir (ejemplo: USDC en MultiversX)
AMOUNT = 1  # Cantidad de EGLD a intercambiar
GAS_LIMIT = 5000000  # Límite de gas ajustable
SC_ADDRESS = "erd1qqqqqqqqqqqqqpgqjz9qzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"  # Dirección del contrato de xExchange

# Inicializar conexión con MultiversX
provider = ProxyNetworkProvider(PROVIDER_URL)

# Cargar cuenta desde clave privada
account = Account(address=ADDRESS)
signer = UserSigner.from_private_key(PRIVATE_KEY)
account.sync_nonce(provider)

# Crear payload para la transacción de swap
function_name = "swapTokensFixedInput"
params = [
    TokenPayment.fungible(TOKEN_IN, AMOUNT * 10**18),  # Cantidad en decimales
    TOKEN_OUT,  # Token de salida
    1,  # MinOutput: el mínimo de tokens de salida que aceptas
]
payload = TransactionPayload(function_name + "@" + "@".join(map(str, params)))

# Crear transacción
transaction = Transaction(
    nonce=account.nonce,
    sender=ADDRESS,
    receiver=SC_ADDRESS,
    value=0,
    gas_limit=GAS_LIMIT,
    data=payload,
    chain_id="1",  # Red principal de MultiversX
)

# Firmar y enviar transacción
transaction.signature = signer.sign(transaction.serialize())
response = provider.send_transaction(transaction)

# Mostrar resultado
print("Swap enviado. Hash de transacción:", response.get("txHash"))
