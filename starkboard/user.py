import os
import json
from app import get_yesterday_block
from starkboard.utils import Requester

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

wallet_key = {
    "ArgentX": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784"],
    "Braavos": ["0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"],
    "All": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784", "0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"]
}

def count_wallet_deployed(wallet_type="All"):
    """
    Retrieve the number of ArgentX or Braavos wallet Deployed
    Braavos key : 0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049
    ArgentX key : 0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784
    """

    fromBlock, toBlock = get_yesterday_block()

    params = {
        "filter": {
            "fromBlock": fromBlock["block_number"], 
            "toBlock": toBlock["block_number"], 
            "page_size": 500,
            "page_number": 0, 
            "keys": wallet_key[wallet_type]
        }
    }

    r = staknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    count_wallet = len(data["events"])
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = staknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        count_wallet += len(data["events"])


    return {
        "deployedWallets": count_wallet
    }
