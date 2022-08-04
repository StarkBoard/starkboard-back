import os
import json
from starkboard.utils import Requester

if os.environ.get("IS_MAINNET") == "True":
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
else:
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

wallet_key = {
    "ArgentX": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784"],
    "Braavos": ["0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"],
    "All": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784", "0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"]
}

def count_wallet_deployed(wallet_type="All", fromBlock=0, toBlock=0):
    """
    Retrieve the number of ArgentX or Braavos wallet Deployed
    Braavos key : 0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049
    ArgentX key : 0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784
    """
    params = {
        "filter": {
            "fromBlock": fromBlock, 
            "toBlock": toBlock, 
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
        "deployed_wallets": count_wallet
    }


def get_wallet_address_deployed(wallet_type="All", fromBlock=0, toBlock=0):
    """
    Retrieve the number of ArgentX or Braavos wallet Deployed
    Braavos key : 0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049
    ArgentX key : 0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784
    """
    params = {
        "filter": {
            "fromBlock": fromBlock, 
            "toBlock": toBlock, 
            "page_size": 1024,
            "page_number": 0, 
            "keys": wallet_key[wallet_type]
        }
    }

    r = staknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    list_wallet_address = [event["from_address"] for event in data["events"]]
    print(f'{len(list_wallet_address)} Wallets found currently...')
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = staknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        list_wallet_address += [event["from_address"] for event in data["events"]]
        print(f'{len(list_wallet_address)} Wallets found currently...')

    return list_wallet_address
