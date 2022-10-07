import json
from decimal import Decimal
from starkboard.constants import LIST_EVENT_KEYS
from starkboard.events.events import filter_events
from starkboard.events.swap import fetch_pool_info#, store_swap_events
#from starkboard.events.transfer import store_transfer_events
from starkboard.constants import TRANSFER_KEY, SWAP_KEY

################################1
#  Available Transactions Keys  #
#################################

def transactions_in_block(block_id="latest", starknet_node=None):
    """
    Retrieve the list of transactions from a given block number
    """
    params = {
        "block_number": block_id
    }
    r = starknet_node.post("", method="starknet_getBlockWithTxs", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]

def get_transfer_transactions_in_block(events):
    """
    Retrieve the list of transfer events in a given block
    """
    transfer_events = filter_events(events, TRANSFER_KEY)
    count_transfer = len(transfer_events)
    return {
        "count_transfer": count_transfer
    }

def get_transactions_info_in_block(events):
    """
    Retrieves count and fees of different transactions types in a block
    """
    tx_info = {}
    for event_name in LIST_EVENT_KEYS.keys():
        if event_name == "Transaction":
            continue
        tx_info[event_name] = {}
    for event in events:
        if event["event_name"] in LIST_EVENT_KEYS.keys() and event["event_name"] != "Transaction":
            tx_hash = event["tx_hash"]
            name = event["event_name"]
            if name == "Transfer" and json.loads(event["data"])["type"] != "Transfer":
                name = json.loads(event["data"])["type"]
            if name == "Approval" or name == "ApprovalForAll" and tx_hash not in list(tx_info["Transfer"].keys()) + list(tx_info["Mint"].keys()) + list(tx_info["Burn"].keys()) + list(tx_info["Deposit"].keys()) + list(tx_info["Withdraw"].keys()) + list(tx_info["PairCreated"].keys()):
                tx_info[name][tx_hash] = event["total_fees"]
            elif name == "Transfer" or name == "TransferBatch":
                tx_info["Approval"].pop(tx_hash, None)
                tx_info["ApprovalForAll"].pop(tx_hash, None)
                if tx_hash not in list(tx_info["Swap"].keys()) + list(tx_info["Mint"].keys()) + list(tx_info["Burn"].keys()) + list(tx_info["Deposit"].keys()) + list(tx_info["Withdraw"].keys()) + list(tx_info["PairCreated"].keys()):
                    tx_info[name][tx_hash] = event["total_fees"]
            elif name != "Approval" and name != "ApprovalForAll":
                tx_info["Approval"].pop(tx_hash, None)
                tx_info["ApprovalForAll"].pop(tx_hash, None)
                tx_info["Transfer"].pop(tx_hash, None)
                tx_info["TransferBatch"].pop(tx_hash, None)
                tx_info[name][tx_hash] = event["total_fees"]
    info = {}
    for event_name in tx_info.keys():
        info["count_" + event_name] = len(tx_info[event_name].keys())
        info["fees_" + event_name] = sum(Decimal(fees) for fees in list(tx_info[event_name].values()))
        # automatize events hierarchy management
    return info


'''
def get_swap_info_in_block(timestamp, events, starknet_node, db, loop):
    """
    Retrieve the list of swaps events in a given block
    """
    swap_events = filter_events(events, SWAP_KEY)
    count_swaps= len(swap_events)
    pool_info = fetch_pool_info(swap_events, starknet_node, db, loop)
    store_swap_events(timestamp, swap_events, pool_info, starknet_node, db)
    return {
        "count_swap": count_swaps
    }
'''

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
            "page_number": 0
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)
    data = data["result"]
    results = {}
    events = data["events"]
    events = list(filter(lambda event: event['keys'] == TRANSFER_KEY, events))
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
        events = list(filter(lambda event: event['keys'] == TRANSFER_KEY, events))
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
