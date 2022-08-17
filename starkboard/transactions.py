import os
import json
from starkboard.utils import Requester
from datetime import datetime, time, timedelta

starknet_events = Requester("http://starknet.events/api/v1/get_events", headers={"Content-Type": "application/json"})


################################1
#  Available Transactions Keys  #
#################################

transaction_executed_key = ["0x5ad857f66a5b55f1301ff1ed7e098ac6d4433148f0b72ebc4a2945ab85ad53"]
transfer_key = ["0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"]


def transactions_in_block(block_id="latest", starknet_node=None):
    """
    Retrieve the list of transactions hash from a given block number
    """
    params = {
        "block_number": block_id
    }
    r = starknet_node.post("", method="starknet_getBlockWithTxs", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]


def get_transfer_transactions_in_block(block, starknet_node):
    """
    Retrieve the list of transfer events in a given block
    """
    params = {
        "filter": {
            "fromBlock": {
                "block_number": block
            }, 
            "toBlock": {
                "block_number": block
            },
            "page_size": 500,
            "page_number": 0, 
            "keys": transfer_key
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    count_transfer = len(data["events"])
    while not data["is_last_page"]:
        print(count_transfer)
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        count_transfer += len(data["events"])
    return {
        "count_transfer": count_transfer
    }

def get_transfer_transactions(fromBlock, toBlock, starknet_node):
    """
    Retrieve the list of transfer events in a given block
    """
    params = {
        "filter": {
            "fromBlock": {
                "block_number": fromBlock
            }, 
            "toBlock": {
                "block_number": toBlock
            },
            "page_size": 1000,
            "page_number": 0, 
            "keys": transfer_key
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    results = {}
    events = data["events"]
    print(f'{len(events)} events fetched.')
    for event in events:
        if event["block_number"] not in results:
            results[event["block_number"]] = 1
        else:
            results[event["block_number"]] += 1
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        events = data["events"]
        print(f'{len(events)} events fetched.')
        for event in events:
            if event["block_number"] not in results:
                results[event["block_number"]] = 1
            else:
                results[event["block_number"]] += 1
    return results



def get_transfer_transactions_v2(fromBlock, toBlock):
    """
    Retrieve the list of transfer events in a given block
    """
    page_number = 1

    query = f'?chain_id=testnet&from_block={fromBlock}&to_block={toBlock}&page={page_number}&size=100&key={transfer_key[0]}'
    r = starknet_events.get(query)
    data = json.loads(r.text)
    results = {}
    events = data["items"]
    for event in events:
        if event["block_number"] not in results:
            results[event["block_number"]] = 1
        else:
            results[event["block_number"]] += 1
    while not len(events) != 100:
        page_number += 1
        query = f'?chain_id=testnet&from_block={fromBlock}&to_block={toBlock}&page={page_number}&size=100&key={transfer_key[0]}'
        r = starknet_events.get(query)
        data = json.loads(r.text)
        events = data["items"]
        for event in events:
            if event["block_number"] not in results:
                results[event["block_number"]] = 1
            else:
                results[event["block_number"]] += 1
    return results
