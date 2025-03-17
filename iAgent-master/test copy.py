import asyncio
from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network

async def main():
    # Forzar testnet como en el resto del código
    network = Network.testnet()
    client = AsyncClient(network=network)
    
    injective_address = "inj1p9frwu0684ryjr9r6xg43d440vz4mhx4h7lzyg"
    
    try:
        # Verificar transacciones usando el método correcto
        txs = await client.fetch_account_txs(injective_address)
        
        # Verificar balance
        balance = await client.fetch_bank_balances(injective_address)
        
        print(f"Verificando dirección: {injective_address}")
        print("---")
        
        # Verificar si hay transacciones
        if txs and 'data' in txs and txs['data']:
            print(f"La dirección tiene {len(txs['data'])} transacciones recientes")
            for tx in txs['data']:
                print(f"Hash: {tx.get('hash', 'No hash')}")
                print(f"Tipo: {tx.get('txType', 'Desconocido')}")
                print(f"Fecha: {tx.get('blockTimestamp', 'Desconocido')}")
                print("---")
        else:
            print("La dirección NO tiene transacciones")
            
        # Verificar balance
        if balance and 'balances' in balance and balance['balances']:
            print("Balances encontrados:")
            for coin in balance['balances']:
                print(f"  {coin.get('amount')} {coin.get('denom')}")
        else:
            print("La dirección NO tiene balance")
            
        # Conclusión
        if (not txs or not txs.get('data')) and (not balance or not balance.get('balances')):
            print("\nCONCLUSIÓN: Esta es una dirección completamente nueva sin actividad")
        else:
            print("\nCONCLUSIÓN: Esta dirección tiene actividad (balance o transacciones)")
        
    except Exception as e:
        print(f"Error al verificar la dirección: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
