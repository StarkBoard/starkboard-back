import json
from starkboard.utils import hex_string_to_decimal

def normalize_transfer(data):
    normalized = {}
    normalized['sender'] = list(filter(lambda x: 'from' in x['name'], data))[0].get('value')
    normalized['receiver'] = list(filter(lambda x: 'to' in x['name'], data))[0].get('value')
    normalized['amount'] = hex_string_to_decimal(list(filter(lambda x: 'value' in x['name'], data))[0].get('value').get('low'))
    return normalized

def normalize_swap(data):
    return data

normalize_switcher = {
    "Transfer": normalize_transfer,
    "Swap": normalize_swap
}


class EventNormalizer:

    def __init__(self, event_name, data):
        self.event_name = event_name
        self.data = data
        self.normalized_data = normalize_switcher[self.event_name](self.data)

    def get_normalized_event(self):
        return self.normalized_data
       