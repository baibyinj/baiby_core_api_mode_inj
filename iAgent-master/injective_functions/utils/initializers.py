from grpc import RpcError
from pyinjective.async_client import AsyncClient
from pyinjective.constant import GAS_FEE_BUFFER_AMOUNT, GAS_PRICE
from pyinjective.core.network import Network
from pyinjective.core.broadcaster import MsgBroadcasterWithPk
from pyinjective.transaction import Transaction
from pyinjective.wallet import PrivateKey
from injective_functions.utils.helpers import detailed_exception_info


class ChainInteractor:
    def __init__(self, network_type: str = "mainnet", private_key: str = None) -> None:
        self.private_key = private_key
        # Forzar testnet
        self.network_type = "testnet"
        
        print(f"DEBUG - Initializing ChainInteractor")
        print(f"DEBUG - Forcing TESTNET mode")
        
        try:
            # Initialize account
            self.priv_key = PrivateKey.from_hex(self.private_key)
            self.pub_key = self.priv_key.to_public_key()
            self.address = self.pub_key.to_address()
            bech32_address = self.address.to_acc_bech32()
            
            # Siempre usar testnet
            print(f"DEBUG - Setting up TESTNET")
            self.network = Network.testnet()
            print(f"DEBUG - TESTNET chain_id: {self.network.chain_id}")
            
            print(f"DEBUG - Network endpoint: {self.network.grpc_endpoint}")
            print(f"DEBUG - Fee denom: {self.network.fee_denom}")
            print(f"DEBUG - Sender address: {bech32_address}")
            
        except Exception as e:
            print(f"DEBUG - Error in initialization: {str(e)}")
            import traceback
            print(f"DEBUG - Full traceback: {traceback.format_exc()}")
            raise

        self.client = None
        self.composer = None
        self.message_broadcaster = None

    async def init_client(self):
        """Initialize the Injective client and required components"""
        print(f"DEBUG - Initializing client for network type: {self.network_type}")
        self.client = AsyncClient(self.network)
        self.composer = await self.client.composer()
        await self.client.sync_timeout_height()
        
        try:
            account_info = await self.client.fetch_account(self.address.to_acc_bech32())
            print(f"DEBUG - Account info fetched: {account_info}")
        except Exception as e:
            print(f"DEBUG - Error fetching account: {str(e)}")
            raise
        
        self.message_broadcaster = MsgBroadcasterWithPk.new_using_simulation(
            network=self.network,
            private_key=self.private_key
        )
        print(f"DEBUG - Client initialized for {self.network.chain_id}")

    async def build_and_broadcast_tx(self, msg):
        """Common function to build and broadcast transactions"""
        try:
            print(f"DEBUG - Building transaction")
            print(f"DEBUG - Message payload: {msg}")
            
            if not self.client:
                await self.init_client()
            
            # Verificar la dirección del remitente
            sender_address = self.address.to_acc_bech32()
            print(f"DEBUG - Verified sender address: {sender_address}")
            
            # Construir la transacción
            tx = (
                Transaction()
                .with_messages(msg)
                .with_sequence(self.client.get_sequence())
                .with_account_num(self.client.get_number())
                .with_chain_id(self.network.chain_id)
            )
            
            # Usar valores de gas basados en la simulación anterior
            gas_wanted = 245350  # Valor obtenido de la simulación
            tx = tx.with_gas(gas_wanted)
            
            # Configurar fee según el requerimiento de la red
            gas_price = 160000000000  # Ajustado para cumplir con el fee mínimo requerido
            initial_fee = [
                self.composer.coin(
                    amount=gas_price * gas_wanted,  # Esto dará aproximadamente 39256000000000 inj
                    denom=self.network.fee_denom
                )
            ]
            tx = tx.with_fee(initial_fee)
            
            print(f"DEBUG - Transaction details:")
            print(f"  - Gas limit: {gas_wanted}")
            print(f"  - Gas price: {gas_price}")
            print(f"  - Total fee: {gas_price * gas_wanted}")
            
            # Obtener y mostrar el balance antes de la transacción
            balance = await self.client.fetch_bank_balances(self.address.to_acc_bech32())
            print(f"DEBUG - Current balance: {balance}")
            
            print(f"DEBUG - Transaction details:")
            print(f"  - Sequence: {self.client.get_sequence()}")
            print(f"  - Account number: {self.client.get_number()}")
            print(f"  - Chain ID: {self.network.chain_id}")
            
            # Simular la transacción primero
            sim_sign_doc = tx.get_sign_doc(self.pub_key)
            sim_sig = self.priv_key.sign(sim_sign_doc.SerializeToString())
            sim_tx_raw_bytes = tx.get_tx_data(sim_sig, self.pub_key)
            
            print(f"DEBUG - Simulation payload:")
            print(f"  - Sign doc: {sim_sign_doc}")
            print(f"  - Signature: {sim_sig.hex()}")
            
            try:
                sim_res = await self.client.simulate(sim_tx_raw_bytes)
                print(f"DEBUG - Simulation result: {sim_res}")
            except Exception as e:
                print(f"DEBUG - Simulation failed: {str(e)}")
                return {"error": f"Simulation failed: {str(e)}"}

            # Configurar gas y fee
            gas_limit = int(sim_res["gasInfo"]["gasUsed"]) * 2
            fee = [
                self.composer.coin(
                    amount=gas_price * gas_limit,
                    denom=self.network.fee_denom,
                )
            ]
            
            tx = tx.with_gas(gas_limit).with_fee(fee)
            print(f"DEBUG - Final transaction details:")
            print(f"  - Gas limit: {gas_limit}")
            print(f"  - Fee: {fee}")
            
            # Firmar y transmitir
            sign_doc = tx.get_sign_doc(self.pub_key)
            sig = self.priv_key.sign(sign_doc.SerializeToString())
            tx_raw_bytes = tx.get_tx_data(sig, self.pub_key)
            
            print(f"DEBUG - Final transaction payload:")
            print(f"  - Sign doc: {sign_doc}")
            print(f"  - Signature: {sig.hex()}")
            print(f"  - Raw bytes length: {len(tx_raw_bytes)}")

            res = await self.client.broadcast_tx_sync_mode(tx_raw_bytes)
            print(f"DEBUG - Broadcast result: {res}")
            return res

        except Exception as e:
            print(f"DEBUG - Transaction failed: {str(e)}")
            import traceback
            print(f"DEBUG - Full traceback: {traceback.format_exc()}")
            return {"error": str(e)}
