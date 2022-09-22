import json
from starkboard.utils import hex_string_to_decimal

def normalize_transfer(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: 'from' in x['name'], data))[0].get('value')
    normalized['receiver'] = list(filter(lambda x: 'to' in x['name'], data))[0].get('value')
    normalized['amount'] = hex_string_to_decimal(list(filter(lambda x: 'value' in x['name'], data))[0].get('value').get('low'))
    if normalized['sender'] == "0x0":
        normalized['type'] = "Mint"
    elif normalized['receiver'] == "0x0":
        normalized['type'] = "Burn"
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
    return data

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
    normalized['receiver'] = list(filter(lambda x: 'to' in x['name'], data))[0].get('value')
    normalized['amount0'] = hex_string_to_decimal(list(filter(lambda x: 'amount0' in x['name'], data))[0].get('value').get('low'))
    normalized['amout1'] = hex_string_to_decimal(list(filter(lambda x: 'amount1' in x['name'], data))[0].get('value').get('low'))
    return normalized

normalize_switcher = {
    "Transfer": normalize_transfer,
    "Swap": normalize_swap,
    "Mint": normalize_mint,
    "Burn": normalize_burn,
    "Sync": normalize_sync
}


class EventNormalizer:

    def __init__(self, event_name, data):
        self.event_name = event_name
        self.data = data
        self.normalized_data = normalize_switcher[self.event_name](self.data)

    def get_normalized_event(self):
        return self.normalized_data
       