import os
import json
from app import get_yesterday_block
from starkboard.utils import Requester

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

def count_contract_deployed():
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """

    fromBlock, toBlock = get_yesterday_block()
    


    return {}


def most_used_functions_from_contract(contract_address):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """

    fromBlock, toBlock = get_yesterday_block()
    


    return {}
