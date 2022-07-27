import os
import json
from starkboard.utils import Requester

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

def count_contract_deployed():
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    r = staknet_node.post("", method="", params=[])



    data = json.loads(r.text)
    return data["result"]