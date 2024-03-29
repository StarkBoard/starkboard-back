import json
import asyncio
import numpy as np
from datetime import datetime
from starkboard.utils import get_swap_amount_info, to_unit
from starkboard.contracts import get_pool_info
from starkboard.fees import get_fees_in_tx
from starkboard.events.events import get_event_structure_from_abi


def fetch_pool_info(swap_events, starknet_node, db, loop):
    pool_contracts = list(set(map(lambda event: event["from_address"], swap_events)))
    pool_info = {}
    group = asyncio.gather(*[get_pool_info(contract, starknet_node, db) for contract in pool_contracts])
    results = loop.run_until_complete(group)
    for idx, contract in enumerate(pool_contracts):
        pool_info[contract] = results[idx]
    return pool_info

'''
def store_swap_events(timestamp, swap_events, pool_info, starknet_node, db):
    for event in swap_events:
        try:
            assert len(event["data"]) == 10
            block_number = event["block_number"]
            event_key = event["keys"][0]
            tx_hash = event["transaction_hash"]
            pair_swapped = event["from_address"]
            sender = event["data"][0]
            user = event["data"][-1]
            event_fees = get_fees_in_tx(tx_hash, starknet_node)
            token_in, token_info_in, amount_in, token_out, token_info_out, amount_out = get_swap_amount_info(event["data"][1:len(event["data"])-1], pool_info[pair_swapped])
            event_data = {
                "timestamp": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "full_day": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                "block_number": block_number,
                "contract_address": pair_swapped,
                "wallet_address": user,
                "event_key": event_key,
                "total_fee": to_unit(event_fees, 18),
                "data": json.dumps({
                    f"{token_in}": to_unit(amount_in, token_info_in.get("decimals")),
                    f"{token_out}": to_unit(amount_out, token_info_out.get("decimals")),
                    "router_address": sender
                })
            }
            db.insert_events(event_data)
        except Exception as e:
            print(f'[❌ NOT STANDARDIZED  {event["block_number"]}] From Contract : {event["from_address"]}')
            continue
    return
'''