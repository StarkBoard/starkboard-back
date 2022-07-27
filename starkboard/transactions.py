import os
import json
from starkboard.utils import Requester

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

def transactions_in_block(block_id="latest"):
    """
    Retrieve the list of transactions hash from a given block number
    """
    r = staknet_node.post("", method="starknet_getBlockByNumber", params=[block_id])
    data = json.loads(r.text)
    return data["result"]


#@TODO
def get_transactions_in_block2(block_id="latest"):
    """
    Retrieve the list of transactions hash from a given block number
    """
    r = staknet_node.post("", method="starknet_getBlockByNumber", params=[block_id])
    data = json.loads(r.text)
    return data["result"]
