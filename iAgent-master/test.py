import asyncio
from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network
import base64
import json

async def main():
    # Forzar testnet como en el resto del código
    network = Network.testnet()
    client = AsyncClient(network=network)
    
    origen_address = "inj1p9frwu0684ryjr9r6xg43d440vz4mhx4h7lzyg"
    destino_address = "inj1pxshsnqhm6z4sgqxehuzqr9fkdzf4ypgtra56a"
    
    try:
        # Verificar transacciones
        txs = await client.fetch_account_txs(origen_address)
        
        print(f"Todas las transacciones encontradas para {origen_address}:")
        print("---")
        
        # Mostrar todas las transacciones
        if txs and 'data' in txs and txs['data']:
            print(f"Total de transacciones: {len(txs['data'])}")
            for tx in txs['data']:
                print(f"Hash: {tx.get('hash')}")
                print(f"Fecha: {tx.get('blockTimestamp')}")
                print("Mensajes (raw):", tx.get('messages', 'No messages'))
                try:
                    # Intentar decodificar el mensaje
                    messages_base64 = tx.get('messages', '')
                    if messages_base64:
                        messages = base64.b64decode(messages_base64)
                        decoded_messages = json.loads(messages)
                        print("Mensajes decodificados:", json.dumps(decoded_messages, indent=2))
                except Exception as e:
                    print(f"Error decodificando mensaje: {str(e)}")
                print("---")
        
        print("\nBuscando transferencias específicas al destino...")
        print(f"Destino: {destino_address}")
        print("---")
        
        transferencias_encontradas = []
        
        # Verificar transferencias específicas
        if txs and 'data' in txs and txs['data']:
            for tx in txs['data']:
                try:
                    messages_base64 = tx.get('messages', '')
                    if messages_base64:
                        messages = base64.b64decode(messages_base64)
                        decoded_messages = json.loads(messages)
                        
                        for msg in decoded_messages:
                            if msg.get('type') == '/cosmos.bank.v1beta1.MsgSend':
                                if msg.get('value', {}).get('to_address') == destino_address:
                                    tx_details = {
                                        'hash': tx.get('hash'),
                                        'fecha': tx.get('blockTimestamp'),
                                        'bloque': tx.get('blockNumber'),
                                        'gas_usado': tx.get('gasUsed'),
                                        'gas_wanted': tx.get('gasWanted'),
                                        'fee': tx.get('gasFee', {}).get('amount', []),
                                        'amount': msg.get('value', {}).get('amount', []),
                                        'estado': 'Exitosa' if tx.get('code', 1) == 0 else 'Fallida'
                                    }
                                    transferencias_encontradas.append(tx_details)
                except Exception as e:
                    print(f"Error al procesar transacción {tx.get('hash')}: {str(e)}")
                    continue
        
        # Mostrar resultados de transferencias específicas
        if transferencias_encontradas:
            print(f"Se encontraron {len(transferencias_encontradas)} transferencias a la dirección destino:")
            for tx in transferencias_encontradas:
                print(f"Hash: {tx['hash']}")
                print(f"Fecha: {tx['fecha']}")
                print(f"Bloque: {tx['bloque']}")
                print(f"Gas usado: {tx['gas_usado']}")
                print(f"Gas solicitado: {tx['gas_wanted']}")
                print(f"Estado: {tx['estado']}")
                print("Fee:")
                for fee in tx['fee']:
                    print(f"  {fee.get('amount')} {fee.get('denom')}")
                print("Monto transferido:")
                for amount in tx['amount']:
                    print(f"  {amount.get('amount')} {amount.get('denom')}")
                print("---")
        else:
            print("No se encontraron transferencias a la dirección destino")
        
    except Exception as e:
        print(f"Error al verificar las transferencias: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
