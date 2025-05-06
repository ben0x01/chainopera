import json

from typing import List
from web3 import AsyncWeb3
from eth_abi import encode, decode
from eth_abi.exceptions import EncodingError, DecodingError, EncodingTypeError
from web3.contract import AsyncContract
from web3.exceptions import TransactionNotFound
from eth_account.messages import encode_defunct


class AsyncWeb3Account:
    def __init__(self, private_key: str, rpc_url: str, explorer_url: str, proxy:str) -> None:
        self.private_key = private_key
        self.__w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url, request_kwargs={"proxy": proxy}))
        self.__wallet = self.__w3.eth.account.from_key(private_key)
        self.rpc_url = rpc_url
        self.explorer_url = explorer_url

    def get_contract(self, contract_address: str, abi: json) -> AsyncContract:
        contract_address = self.__w3.to_checksum_address(contract_address)
        contract = self.__w3.eth.contract(address=contract_address, abi=abi)
        return contract

    async def get_balance(self, abi: json=None, contract_address: str=None) -> int:
        if contract_address is None:
            return await self.__w3.eth.get_balance(self.__wallet.address)
        else:
            contract = self.get_contract(contract_address, abi)

            balance = contract.functions.balanceOf(self.__wallet.address).call()
            decimals = contract.functions.decimals().call()
            normalized_balance = balance / (10 ** decimals)
            return normalized_balance


    async def get_data_for_tx(self, increase_factor: float) -> dict:
        nonce = await self.__w3.eth.get_transaction_count(self.__wallet.address, "pending")
        base_fee = await self.__w3.eth.gas_price
        max_priority_fee_per_gas = await self.__w3.eth.max_priority_fee
        max_priority_fee_per_gas = int(max_priority_fee_per_gas * increase_factor)
        max_fee_per_gas = int((base_fee + max_priority_fee_per_gas) * increase_factor)
        chain_id = await self.__w3.eth.chain_id

        return {
            "nonce": nonce,
            "max_fee_per_gas": max_fee_per_gas,
            "max_priority_fee_per_gas": max_priority_fee_per_gas,
            "chainId": chain_id,
        }

    async def _sign_and_send_tx(self, tx: dict) -> str:
        signed_tx = self.__w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = await self.__w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash.hex()


    async def _check_tx_status(self, tx_hash: str) -> bool:
        try:
            receipt = await self.__w3.eth.get_transaction_receipt(tx_hash)
            return receipt['status'] == 1
        except TransactionNotFound:
            return False

    @staticmethod
    def encode_calldata(function_selector: str, types: list, params: list) -> str:
        try:
            encoded_data = encode(types, params).hex()
        except (EncodingError, EncodingTypeError):
            return ""
        return function_selector + encoded_data

    @staticmethod
    def decode_calldata(types: List[str], encoded_data: str) -> dict:
        function_selector = encoded_data[:10]
        try:
            decoded_data = decode(types, bytes.fromhex(encoded_data[10:]))
        except DecodingError:
            return {}
        return {function_selector: decoded_data}

    async def send_transaction(self, transaction):
        tx_hash = await self._sign_and_send_tx(transaction)

        return await self._check_tx_status(tx_hash)

    async def make_contract(self, abi, bytecode):
        return self.__w3.eth.contract(abi=abi, bytecode=bytecode)

    async def get_gas_price(self):
        return await self.__w3.eth.gas_price

    async def get_estimate_gas(self, transaction):
        return await self.__w3.eth.estimate_gas(transaction)

    async def generate_wallet(self) -> str:
        return self.__w3.eth.account.create().address

    def get_wallet_address(self):
        return self.__wallet.address

    def checksum_address(self, address: str):
        return self.__w3.to_checksum_address(address)

    async def sign_mess(self, message: str):
        encoded_mesage = encode_defunct(text=message)

        signed_message = self.__wallet.sign_message(encoded_mesage)

        return "0x" + signed_message.signature.hex()

