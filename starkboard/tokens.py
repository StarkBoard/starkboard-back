import os
import json
from starkboard.utils import Requester
from datetime import datetime, time, timedelta
from starknet_py.contract import Contract
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.networks import TESTNET
from starknet_py.cairo.felt import decode_shortstring
from starknet_py.net.account.account_client import AccountClient
from starknet_py.net.signer import BaseSigner

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
client = GatewayClient(TESTNET)


################################1
#  Available Transactions Keys  #
#################################

token_addresses = {
    "ETH": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
    "DAI": "0x03e85bfbb8e2a42b7bead9e88e9a1b19dbccf661471061807292120462396ec9",
    "WBTC":"0x12d537dc323c439dc65c976fad242d5610d27cfb5f31689a0a319b8be7f3d56",
    "USDC": "0x005a643907b9a4bc6a55e9069c4fd5fd1f5c79a22470690f75556c4736e34426"
}


async def get_eth_total_supply():
    """
    Retrieve ETH token total supply
    """
    #21340212719716957978097
    with open("abi/ERC20.json") as jsonFile:
        abi = json.load(jsonFile)
        jsonFile.close()
    contract = Contract(address=token_addresses["ETH"], abi=abi, client=client)
    (name,) = await contract.functions["name"].call()
    (supply,) = await contract.functions["totalSupply"].call()
    print(f'Total Supply of {decode_shortstring(name)} : {supply / 10**18}')
        

async def get_balance_of(wallet_address, token_name="ETH"):
    """
    Retrieve ETH token total supply
    """
    with open("abi/ERC20.json") as jsonFile:
        abi = json.load(jsonFile)
        jsonFile.close()
    accountContract = AccountClient(address=wallet_address, client=client, signer=BaseSigner)
    try:
        balance = await accountContract.get_balance(token_addresses[token_name])
    except Exception as e:
        balance = 0
    return balance / 10**18
