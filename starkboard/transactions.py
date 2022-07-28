import os
import json
from app import get_yesterday_block
from starkboard.utils import Requester
from datetime import datetime, time, timedelta

staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

################################1
#  Available Transactions Keys  #
#################################

transaction_executed_key = ["0x5ad857f66a5b55f1301ff1ed7e098ac6d4433148f0b72ebc4a2945ab85ad53"]
transfer_key = ["0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"]


def transactions_in_block(block_id="latest"):
    """
    Retrieve the list of transactions hash from a given block number
    """
    r = staknet_node.post("", method="starknet_getBlockByNumber", params=[block_id])
    data = json.loads(r.text)
    return data["result"]


def get_transfer_transactions_in_block():
    """
    Retrieve the list of transactions hash from a given block number
    """
    fromBlock, toBlock = get_yesterday_block()
    params = {
        "filter": {
            "fromBlock": fromBlock["block_number"], 
            "toBlock": toBlock["block_number"], 
            "page_size": 1000,
            "page_number": 0, 
            "keys": transfer_key
        }
    }
    r = staknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    count_transfer = len(data["events"])
    
    while not data["is_last_page"]:
        print(count_transfer)
        params["filter"]["page_number"] += 1
        r = staknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        count_transfer += len(data["events"])

    today = datetime.now()
    last_day = today - timedelta(days=1)
    return {
        "day": last_day.strftime("%m/%d/%Y"),
        "transferCount": count_transfer
    }

