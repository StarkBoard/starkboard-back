import os
import json
from starkboard.constants import LIST_EVENT_KEYS, EVENT_KEYS, CLASS_HASH_TYPE, APP_NAME


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


def count_contract_deployed_in_block(block_txs):
    """
    Retrieve the number of deployed contracts on StarkNet
    """
    deploy_tx = [tx for tx in block_txs if tx["type"] == "DEPLOY"]
    return {
        "count_deployed_contracts": len(deploy_tx)
    }


def most_used_functions_from_contract(block_txs):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    deploy_tx = [tx for tx in block_txs if tx["type"] == "DEPLOY"]


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
    for typed in EVENT_KEYS:
        if all(a in list_functions for a in typed[0]):
            if typed[1] == "ERC20": 
                is_liquidity_pool = list(filter(lambda x: "swap" in x, list_functions))
                if is_liquidity_pool:
                    return "ERC20-LP", typed[2]+LIST_EVENT_KEYS["Swap"]
                else:
                    return typed[1], typed[2]
            else:
                return typed[1], typed[2]
    return None, None

def get_hash_contract_info(type):
    event_keys = CLASS_HASH_TYPE[type][2]
    if type == "ERC20-LP":
        return type, event_keys+LIST_EVENT_KEYS["Swap"]
    else:
        return type, event_keys

def get_application_name(type):
    return APP_NAME.get(type, "Unknown")

def index_deployed_contract(db):
    return {}
