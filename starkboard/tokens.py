import os
import json
from starkboard.utils import Requester
from datetime import datetime, time, timedelta
from starknet_py.contract import Contract
from starknet_py.net.full_node_client import FullNodeClient

from starknet_py.net.networks import TESTNET, MAINNET
from starknet_py.cairo.felt import decode_shortstring
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.signer import BaseSigner


if os.environ.get("IS_MAINNET") == "True":
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
else:
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

abi = None
with open("abi/ERC20.json") as jsonFile:
    abi = json.load(jsonFile)
    jsonFile.close()

################################1
#  Available Transactions Keys  #
#################################

token_addresses = {
    "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    "DAI": "0x03e85bfbb8e2a42b7bead9e88e9a1b19dbccf661471061807292120462396ec9",
    "WBTC":"0x12d537dc323c439dc65c976fad242d5610d27cfb5f31689a0a319b8be7f3d56",
    "USDC": "0x005a643907b9a4bc6a55e9069c4fd5fd1f5c79a22470690f75556c4736e34426"
}


async def get_eth_total_supply(network="testnet"):
    """
    Retrieve ETH token total supply
    """
    #21340212719716957978097
    if network == "mainnet": 
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL_MAINNET'), MAINNET)
    else:
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL'), TESTNET)
    contract = Contract(address=token_addresses["ETH"], abi=abi, client=client)
    (name,) = await contract.functions["name"].call()
    (supply,) = await contract.functions["totalSupply"].call()
    print(f'Total Supply of {decode_shortstring(name)} : {supply / 10**18}')
        

def get_balance_of(wallet_address, network="testnet"):
    """
    Retrieve ETH token total supply
    """
    if network == "mainnet": 
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL_MAINNET'), MAINNET)
    else:
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL'), TESTNET)
    accountContract = AccountClient(address=int(wallet_address, 16), client=client, signer=BaseSigner)   
    eth_contract = Contract(address=int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16), abi=abi, client=client)
    try:
        #balance = (eth_contract.functions["balanceOf"].call(int(wallet_address, 16))).balance
        balance = accountContract.get_balance_sync(int("0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7", 16))
    except Exception as e:
        print(e)
        balance = 0
    return balance / 10**18


def get_nonce_of(wallet_address, network="testnet"):
    """
    Retrieve ETH token total supply
    """
    if network == "mainnet": 
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL_MAINNET'), MAINNET)
    else:
        client = FullNodeClient(os.environ.get('STARKNET_NODE_URL'), TESTNET)
    accountContract = AccountClient(address=int(wallet_address, 16), client=client, signer=BaseSigner)    
    try:
        nonce = accountContract._get_nonce_sync()
    except Exception as e:
        print("NonceErr.")
        print(e)
        nonce = 0
    return nonce
