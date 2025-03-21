from typing import Dict
from injective_functions.utils.initializers import ChainInteractor
from injective_functions.account import InjectiveAccounts
from injective_functions.auction import InjectiveAuction
from injective_functions.authz import InjectiveAuthz
from injective_functions.bank import InjectiveBank
from injective_functions.exchange.exchange import InjectiveExchange
from injective_functions.exchange.trader import InjectiveTrading
from injective_functions.staking import InjectiveStaking
from injective_functions.token_factory import InjectiveTokenFactory


class InjectiveClientFactory:
    """Factory for creating Injective client instances."""

    @staticmethod
    async def create_all(
        private_key: str, 
        network_type: str = "testnet", 
        api_url: str = "http://localhost:8000/agent/transaction/"
    ) -> Dict:
        """
        Create instances of all Injective modules sharing one ChainInteractor.

        Args:
            private_key (str): Private key for blockchain interactions
            network_type (str, optional): Network type. Defaults to "mainnet".
            api_url (str, optional): API URL for InjectiveBank. Defaults to "http://localhost:8000/agent/transaction/.

        Returns:
            Dict: Dictionary containing all initialized clients
        """
        try:
            print(f"DEBUG - [InjectiveClientFactory.create_all] Starting client creation")
            print(f"  - Network type: {network_type}")
            print(f"  - API URL: {api_url}")
            
            network_type = "testnet"
            print(f"DEBUG - [InjectiveClientFactory.create_all] Forced testnet mode")
            
            chain_client = ChainInteractor(
                network_type=network_type,
                private_key=private_key
            )
            
            # Solo inicializar una vez
            if not chain_client.client:
                print(f"DEBUG - Initializing client for network: {network_type}")
                await chain_client.init_client()
                print(f"DEBUG - Chain client initialized successfully for {network_type}")
            
            clients = {
                "bank": InjectiveBank(chain_client, api_url=api_url),
                "account": InjectiveAccounts(chain_client),
                "auction": InjectiveAuction(chain_client),
                "authz": InjectiveAuthz(chain_client),
                "exchange": InjectiveExchange(chain_client),
                "trader": InjectiveTrading(chain_client),
                "staking": InjectiveStaking(chain_client),
                "token_factory": InjectiveTokenFactory(chain_client)
            }
            
            print(f"DEBUG - Created all clients for network: {chain_client.network.chain_id}")
            return clients
            
        except Exception as e:
            print(f"DEBUG - Error creating clients: {str(e)}")
            import traceback
            print(f"DEBUG - Full traceback: {traceback.format_exc()}")
            raise
