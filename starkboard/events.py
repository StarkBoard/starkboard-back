import json
import numpy as np
from starkboard.utils import get_swap_amount_info
from starkboard.contracts import get_contract_info, get_pool_info

def get_events(block_number, starknet_node):
    """
    Retrieve the list of transfer events in a given block
    """
    params = {
        "filter": {
            "fromBlock": {
                "block_number": block_number
            }, 
            "toBlock": {
                "block_number": block_number
            },
            "page_size": 1000,
            "page_number": 0
        }
    }
    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)
    data = data["result"]
    events = data["events"]
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        events += data["events"]
    print(f'{len(events)} events fetched.')
    return events

def filter_events(events, keys):
    filtered_events = list(filter(lambda event: event['keys'][0] in keys, events))
    return filtered_events

def store_swap_events(swap_events, starknet_node, db):
    pool_contracts = list(set(map(lambda event: event["from_address"], swap_events)))
    pool_info = {contract_address: get_pool_info(contract_address, starknet_node, db) for contract_address in pool_contracts}
    print(pool_info)
    for event in swap_events:
        try:
            assert len(event["data"]) == 10
            block_number = event["block_number"]
            pair_swapped = event["from_address"]
            sender = event["data"][0]
            user = event["data"][-1]
            token_in, amount_in, token_out, amount_out = get_swap_amount_info(event["data"][1:len(event["data"])-1], pool_info[pair_swapped])

            #Store Swap Event
            #Get Volume
            #Get Fees
            print('-------')
            print(f'[{block_number}] : Swapped pool {pair_swapped[:9]}... by {user[:9]}...')
            print(f'    > {amount_in} {token_in} for {amount_out} {token_out}')

        except:
            print(f'[❌ NOT STANDARDIZED]Swap From Contract : {event["from_address"]} at {event["block_number"]}')
            print(event["data"])
            continue
    return
