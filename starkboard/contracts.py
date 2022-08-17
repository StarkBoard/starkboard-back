import os
import json
from starkboard.utils import Requester


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


def most_used_functions_from_contract(contract_address):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """


    


    return {}
