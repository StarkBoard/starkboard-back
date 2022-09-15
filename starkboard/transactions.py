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
swap_key = ["0xe316f0d9d2a3affa97de1d99bb2aac0538e2666d0d8545545ead241ef0ccab"]
mint_key = ["0x34e55c1cd55f1338241b50d352f0e91c7e4ffad0e4271d64eb347589ebdfd16"]
approval_key = ["0x134692b230b9e1ffa39098904722134159652b09c5bc41d88d6698779d228ff"]
burn_key = ["0x243e1de00e8a6bc1dfa3e950e6ade24c52e4a25de4dee7fb5affe918ad1e744"]
sync_key = ["0xe14a408baf7f453312eec68e9b7d728ec5337fbdf671f917ee8c80f3255232"]

list_event_keys = {
    "Transaction": transaction_executed_key,
    "Transfer": transfer_key,
    "Swap": swap_key,
    "Mint": mint_key,
    "Approval": approval_key,
    "Burn": burn_key,
    "Sync": sync_key
}


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
            "page_size": 100,
            "page_number": 0, 
            "keys": transfer_key
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    count_transfer = len(data["events"])
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        count_transfer += len(data["events"])
    return {
        "count_transfer": count_transfer
    }


def get_transfer_transactions_in_block_v2(block, starknet_node):
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
            "page_size": 200,
            "page_number": 0
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    events = data["events"]
    events = list(filter(lambda event: event['keys'] == transfer_key, events))
    count_transfer = len(events)
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        events = data["events"]
        events = list(filter(lambda event: event['keys'] == transfer_key, events))
        count_transfer += len(events)
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
    data = json.loads(r.text)
    data = data["result"]
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


def get_transfer_transactions_v2(fromBlock, toBlock, starknet_node):
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
            "page_number": 0
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)
    data = data["result"]
    results = {}
    events = data["events"]
    events = list(filter(lambda event: event['keys'] == transfer_key, events))
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
        events = list(filter(lambda event: event['keys'] == transfer_key, events))
        print(f'{len(events)} events fetched.')
        for event in events:
            if event["block_number"] not in results:
                results[event["block_number"]] = 1
            else:
                results[event["block_number"]] += 1
    return results


def state_update(block_id="latest", starknet_node=None):
    """
    Retrieve the list of transactions hash from a given block number
    """
    if block_id != "latest":
        params = {
            "block_number": block_id
        }
    else:
        params = block_id
    r = starknet_node.post("", method="starknet_getStateUpdate", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]['state_diff']
