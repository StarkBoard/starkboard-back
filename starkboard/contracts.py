import os
import json
from starkboard.utils import Requester
from starkboard.transactions import list_event_keys

ERC20_STD = [
    ["name", "symbol", "decimals", "balanceOf", "totalSupply", "approve", "transfer"], 
    "ERC20",
    [list_event_keys["Transfer"], list_event_keys["Approval"], list_event_keys["Mint"], list_event_keys["Burn"]]
]
ERC721_STD = [
    ["name", "symbol", "tokenURI", "approve", "ownerOf"], 
    "ERC721",
    [list_event_keys["Transfer"], list_event_keys["Approval"], list_event_keys["Mint"], list_event_keys["Burn"]],
]
ERC1155_STD = [
    ["balanceOf", "balanceOfBatch"],
    "ERC1155",
    [list_event_keys["Transfer"], list_event_keys["Approval"], list_event_keys["Mint"], list_event_keys["Burn"]]
]
ACCOUNT_STD = [
    ["__execute__", "supportsInterface"], 
    "Account",
    [list_event_keys["Transfer"]]
]
ROUTER_STD = [
    ["Router", "swap"], 
    "Router",
    []
]
JEDISWAPLP_STD = [
    ["Swap", "Mint", "IJediSwapCallee"], 
    "Router",
    [list_event_keys["Mint"], list_event_keys["Burn"], list_event_keys["Swap"], list_event_keys["Sync"]]
]


class_hashes_types = {
    "ERC20": ERC20_STD,
    "ERC20-LP": ERC20_STD,
    "ERC20-LP-JediSwap": JEDISWAPLP_STD,
    "Router": ROUTER_STD,
    "ERC721": ERC721_STD,
    "ERC1155": ERC1155_STD,
    "Account": ACCOUNT_STD
}

app_name = {
    "ERC20-LP-JediSwap": "JediSwap"
}

def count_contract_deployed_current_block(starknet_node, starknet_gateway):
    """
    Retrieve the number of deployed contracts on StarkNet
    """
    r = starknet_node.post("", method="starknet_blockNumber", params=[])
    block_number = json.loads(r.text)["result"]  
    transactions = json.loads(starknet_gateway.get(f"get_block?blockNumber={block_number}").text)
    deploy_tx = [tx for tx in transactions["transactions"] if tx["type"] == "DEPLOY"]
    return {
        "countDeployedContract": len(deploy_tx)
    }


def count_contract_deployed_in_block(block_transactions):
    """
    Retrieve the number of deployed contracts on StarkNet
    """
    deploy_tx = [tx for tx in block_transactions["transactions"] if tx["type"] == "DEPLOY"]
    return {
        "count_deployed_contracts": len(deploy_tx)
    }


def most_used_functions_from_contract(block_transactions):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    deploy_tx = [tx for tx in block_transactions["transactions"] if tx["type"] == "DEPLOY"]


    return {}


def get_class_program(class_hash, starknet_node=None):
    """
    Retrieve the list of transactions hash from a given block number
    """
    params = class_hash
    r = starknet_node.post("", method="starknet_getClass", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]['program']


def classify_hash_contract(list_functions):
    for typed in [JEDISWAPLP_STD, ERC20_STD, ERC1155_STD, ERC721_STD, ACCOUNT_STD, ROUTER_STD]:
        if all(a in list_functions for a in typed[0]):
            if typed[1] == "ERC20": 
                is_liquidity_pool = list(filter(lambda x: "swap" in x, list_functions))
                if is_liquidity_pool:
                    return "ERC20-LP", typed[2]+list_event_keys["Swap"]
                else:
                    return typed[1], typed[2]
            else:
                return typed[1], typed[2]
    return None, None

def get_hash_contract_info(type):
    event_keys = class_hashes_types[type][2]
    if type == "ERC20-LP":
        return type, event_keys+list_event_keys["Swap"]
    else:
        return type, event_keys

def get_application_name(type):
    return app_name.get(type, "Unknown")

def index_deployed_contract(db):


    return {}