import os
import json
from starkboard.utils import Requester


if os.environ.get("IS_MAINNET") == "True":
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
    starknet_gateway = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL_MAINNET"), headers={"Content-Type": "application/json"})
else:
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    starknet_gateway = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})


def count_contract_deployed_current_block():
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    r = staknet_node.post("", method="starknet_blockNumber", params=[])
    block_number = json.loads(r.text)["result"]  
    transactions = json.loads(starknet_gateway.get(f"get_block?blockNumber={block_number}").text)
    deploy_tx = [tx for tx in transactions["transactions"] if tx["type"] == "DEPLOY"]
    return {
        "countDeployedContract": len(deploy_tx)
    }


def count_contract_deployed_int_block(block):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    transactions = json.loads(starknet_gateway.get(f"get_block?blockNumber={block}").text)
    deploy_tx = [tx for tx in transactions["transactions"] if tx["type"] == "DEPLOY"]
    return {
        "count_deployed_contracts": len(deploy_tx)
    }


def most_used_functions_from_contract(contract_address):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """


    


    return {}
