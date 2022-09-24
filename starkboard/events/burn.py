from datetime import datetime
from starkboard.fees import get_fees_in_tx

def store_burn_events(timestamp, burn_events, starknet_node, db):
    for event in burn_events:
        try:
            assert len(event["data"]) == 10
            block_number = event["block_number"]
            event_key = event["keys"][0]
            tx_hash = event["transaction_hash"]
            token_transferred = event["from_address"]
            user = event["data"][0]
            event_fees = get_fees_in_tx(tx_hash, starknet_node)
            value = event["data"][2]
            print('-------')
            print(tx_hash)
            print(f'[{block_number}] : {value} ETH burned by {user}')
            print(f'    > User paid {event_fees} WEI of fees')
            event_data = {
                "timestamp": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                "full_day": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                "block_number": block_number,
                "contract_address": token_transferred,
                "wallet_address": user,
                "event_key": event_key,
                "total_fee": to_unit(event_fees, 18),
#                "data": json.dumps({
#                    f"{token_in}": to_unit(amount_in, token_info_in.get("decimals")),
#                    f"{token_out}": to_unit(amount_out, token_info_out.get("decimals")),
#                    "router_address": sender
#                })
            }
            db.insert_events(event_data)
        except Exception as e:
            print(f'[❌ NOT STANDARDIZED {event["block_number"]}] Key: {event["keys"][0]} From Contract: {event["from_address"]}')
    return