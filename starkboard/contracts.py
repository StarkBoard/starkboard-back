import os
import json
from starkboard.utils import Requester

ERC20_STD = [["name", "symbol", "decimals", "balanceOf", "totalSupply", "approve", "transfer"], "ERC20"]
ERC721_STD = [["name", "symbol", "tokenURI", "approve", "ownerOf"], "ERC721"]
ERC1155_STD = [["balanceOf", "balanceOfBatch"], "ERC1155"]
ACCOUNT_STD = [["__execute__", "supportsInterface"], "ACCOUNT"]

class_hashes = []

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


def classify_hash_contract(class_hash, list_functions):
    for typed in [ERC20_STD, ERC1155_STD, ERC721_STD, ACCOUNT_STD]:
        if all(a in list_functions for a in typed[0]):
            if typed[1] == "ERC20": 
                is_liquidity_pool = list(filter(lambda x: "swap" in x, list_functions))
                if is_liquidity_pool:
                    print(f'{class_hash} IS A ERC20-LP')
                    return "ERC20-LP"
                else:
                    print(f'{class_hash} IS A {typed[1]}')
                    return typed[1]
            else:
                print(f'{class_hash} IS A {typed[1]}')
                return typed[1]
    #print(f'{class_hash} IS OTHER TYPE, FUNCTIONS IS : ')
    #print(list_functions)
    return "UNKNOWN"


def index_deployed_contract(db):


    return {}