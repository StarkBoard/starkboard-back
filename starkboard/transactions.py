import json
from starkboard.events import filter_events
from starkboard.constants import TRANSFER_KEY

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
