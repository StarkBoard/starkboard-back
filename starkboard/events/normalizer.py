import json
from starkboard.utils import hex_string_to_decimal

def normalize_transfer(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: any(a in x["name"] for a in ["from", "sender"]), data))[0].get('value')
    normalized['receiver'] = list(filter(lambda x: any(a == x["name"] for a in ["recipient", "to", "to_", "_to", "to_address"]), data))[0].get('value')
    try:
        normalized['amount'] = hex_string_to_decimal(list(filter(lambda x: any(a in x["name"] for a in ["value", "amount"]), data))[0].get('value').get('low'))
    except:
        normalized['token_id'] = hex_string_to_decimal(list(filter(lambda x: 'token' in x['name'], data))[0].get('value').get('low'))
    if normalized['sender'] == "0x0":
        normalized['type'] = "Mint"
    elif normalized['receiver'] == "0x0":
        normalized['type'] = "Burn"
    elif normalized.get('token_id'):
        normalized['type'] = "ERC721Transfer"
    else:
        normalized['type'] = "Transfer"
    return normalized

def normalize_swap(data):
    normalized = {}
    normalized['wallet_address'] = list(filter(lambda x: 'to' in x['name'], data))[0].get('value')
    normalized['amount_0_in'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["amount", "0", "in"]) , data))[0].get('value').get('low'))
    normalized['amount_1_in'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["amount", "1", "in"]) , data))[0].get('value').get('low'))
    normalized['amount_0_out'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["amount", "0", "out"]) , data))[0].get('value').get('low'))
    normalized['amount_1_out'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["amount", "1", "out"]) , data))[0].get('value').get('low'))
    return normalized


def normalize_mint(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: 'sender' in x['name'], data))[0].get('value')
    normalized['amount0'] = hex_string_to_decimal(list(filter(lambda x: 'amount0' in x['name'], data))[0].get('value').get('low'))
    normalized['amout1'] = hex_string_to_decimal(list(filter(lambda x: 'amount1' in x['name'], data))[0].get('value').get('low'))
    return normalized

def normalize_burn(data):
    normalized = {}
    normalized['receiver'] = list(filter(lambda x: 'to' in x['name'], data))[0].get('value')
    normalized['amount0'] = hex_string_to_decimal(list(filter(lambda x: 'amount0' in x['name'], data))[0].get('value').get('low'))
    normalized['amout1'] = hex_string_to_decimal(list(filter(lambda x: 'amount1' in x['name'], data))[0].get('value').get('low'))
    return normalized

def normalize_sync(data):
    normalized = {}
    try:
        normalized['reserve0'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["reserve", "0"]), data))[0].get('value'))
        normalized['reserve1'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["reserve", "1"]), data))[0].get('value'))
    except:
        normalized['reserve0'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["reserve", "0"]), data))[0].get('value').get('low'))
        normalized['reserve1'] = hex_string_to_decimal(list(filter(lambda x: all(a in x['name'].lower() for a in ["reserve", "1"]), data))[0].get('value').get('low'))
    return normalized

def normalize_deposit(data):
    normalized = {}
    normalized['caller'] = list(filter(lambda x: 'caller' in x['name'], data))[0].get('value')
    normalized['wallet_address_owner'] = list(filter(lambda x: 'owner' in x['name'], data))[0].get('value')
    normalized['assets'] = hex_string_to_decimal(list(filter(lambda x: 'assets' in x['name'], data))[0].get('value').get('low'))
    normalized['shares'] = hex_string_to_decimal(list(filter(lambda x: 'shares' in x['name'], data))[0].get('value').get('low'))
    return normalized

def normalize_transfer_single(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: any(a in x["name"] for a in ["from", "sender"]), data))[0].get('value')
    normalized['receiver'] = list(filter(lambda x: any(a == x["name"] for a in ["recipient", "to", "to_", "_to", "to_address"]), data))[0].get('value')
    normalized['caller'] = list(filter(lambda x: 'operator' in x['name'], data))[0].get('value')
    normalized['amount'] = hex_string_to_decimal(list(filter(lambda x: 'amount' in x['name'], data))[0].get('value').get('low'))
    normalized['token_id'] = hex_string_to_decimal(list(filter(lambda x: 'token' in x['name'], data))[0].get('value').get('low'))
    return normalized

def normalize_transfer_batch(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: any(a in x["name"] for a in ["from", "sender"]), data))[0].get('value')
    normalized['receiver'] = list(filter(lambda x: any(a == x["name"] for a in ["recipient", "to", "to_", "_to", "to_address"]), data))[0].get('value')
    normalized['caller'] = list(filter(lambda x: 'operator' in x['name'], data))[0].get('value')
    normalized['ids'] = list(filter(lambda x: 'ids' in x['name'], data))[0].get('value')
    normalized['ids'] = [hex_string_to_decimal(id_.get('low')) for id_ in normalized['ids']]
    normalized['amounts'] = list(filter(lambda x: 'amounts' in x['name'], data))[0].get('value')
    normalized['amounts'] = [hex_string_to_decimal(amount.get('low')) for amount in normalized['amounts']]
    return normalized

normalize_switcher = {
    "Transfer": normalize_transfer,
    "TransferSingle": normalize_transfer_single,
    "TransferBatch": normalize_transfer_batch,
    "Swap": normalize_swap,
    "Mint": normalize_mint,
    "Burn": normalize_burn,
    "Sync": normalize_sync,
    "Deposit": normalize_deposit
}

class EventNormalizer:

    def __init__(self, event_name, data):
        self.event_name = event_name
        self.data = data
        try:
            self.normalized_data = normalize_switcher[self.event_name](self.data)
        except Exception as e:
            print(e)
            self.normalized_data = data

    def get_normalized_event(self):
        return self.normalized_data
       