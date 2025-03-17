from typing import Dict, Any
import aiohttp
from decimal import Decimal
from injective_functions.base import InjectiveBase
import inspect

class TransactionBabysitter(InjectiveBase):
    def __init__(self, chain_client, api_url: str) -> None:
        print(f"DEBUG - [TransactionBabysitter.__init__] Starting initialization")
        super().__init__(chain_client)
        self.api_url = api_url
        print(f"DEBUG - [TransactionBabysitter.__init__] Initialized with API URL: {api_url}")

    async def validate_with_api(
        self,
        tx_payload: Dict[str, Any],
        chat_history: list,
        sender: str,
        recipient: str,
        amount: Decimal,
        denom: str
    ) -> Dict[str, bool]:
        try:
            print(f"DEBUG - [TransactionBabysitter.validate_with_api] Starting validation")
            print(f"  - API URL: {self.api_url}")
            
            # Extraer todos los mensajes del usuario del chat_history
            user_messages = [msg["content"] for msg in chat_history if msg.get("role") == "user"]
            full_conversation = " | ".join(user_messages)
            
            # El amount ya viene en formato decimal (ej: 0.01), no necesitamos convertirlo
            #formatted_amount = "{:.2f}".format(float(amount))
            #print(formatted_amount)
            
            # Crear el mensaje con el amount formateado
            msg_data = f'from_address: "{sender}"\nto_address: "{recipient}"\namount {{\n  denom: "{denom.lower()}"\n  amount: "{amount}"\n}}\n'
            
            validation_data = {
                "safeAddress": sender,
                "erc20TokenAddress": denom,
                "reason": full_conversation,
                "transactions": [{
                    "to": recipient,
                    "data": msg_data,
                    "value": str(amount)
                }]
            }
            
            print(f"DEBUG - Validation data: {validation_data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=validation_data) as response:
                    print(f"DEBUG - API Response status: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"DEBUG - API Response: {result}")
                        return result
                    
                    error_text = await response.text()
                    print(f"DEBUG - API Error: {error_text}")
                    return {
                        "approved": False,
                        "reason": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            print(f"DEBUG - Validation error: {str(e)}")
            return {
                "approved": False,
                "reason": f"Validation error: {str(e)}"
            }

    async def safe_transfer(
        self,
        amount: Decimal,
        denom: str,
        to_address: str,
        chat_history: list
    ) -> Dict:
        try:
            print(f"DEBUG - Babysitter safe_transfer initiated")
            
            # Crear el mensaje de la transacción
            msg = self.chain_client.composer.MsgSend(
                from_address=self.chain_client.address.to_acc_bech32(),
                to_address=str(to_address),
                amount=float(amount),
                denom=denom
            )
            
            print(f"DEBUG - Transaction message created")
            print(f"DEBUG - Message details: {msg}")

            # Validar con la API
            validation = await self.validate_with_api(
                tx_payload=str(msg),
                chat_history=chat_history,
                sender=self.chain_client.address.to_acc_bech32(),
                recipient=to_address,
                amount=amount,
                denom=denom
            )

            print(f"DEBUG - Validation result: {validation}")

            # Verificar si la transacción está aprobada
            if (validation.get("status") == "success" and 
                "APPROVED" in validation.get("message", "")):
                print(f"DEBUG - Transaction approved by babysitter, proceeding with broadcast")
                # Si la validación es exitosa, ejecutar la transacción
                return await self.chain_client.build_and_broadcast_tx(msg)
            else:
                print(f"DEBUG - Transaction rejected by babysitter")
                return {
                    "success": False,
                    "error": f"Transaction rejected: {validation.get('message', 'Unknown reason')}"
                }

        except Exception as e:
            print(f"DEBUG - Safe transfer error: {str(e)}")
            import traceback
            print(f"DEBUG - Full safe_transfer traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Transaction failed: {str(e)}"
            } 