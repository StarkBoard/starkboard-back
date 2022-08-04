import os
import json
from starkboard.utils import Requester

if os.environ.get("IS_MAINNET") == "True":
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
else:
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

def estimate_fees():
    """
    Retrieve the list of transactions hash from a given block number
    """
    r = staknet_node.post("", method="starknet_estimateFee", params=[])
    data = json.loads(r.text)
    return data