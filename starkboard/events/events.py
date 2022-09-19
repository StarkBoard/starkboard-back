import json
from starkware.starknet.compiler.compile import get_selector_from_name
from starkboard.contracts import get_contract_info

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
    return events

def filter_events(events, keys):
    filtered_events = list(filter(lambda event: event['keys'][0] in keys, events))
    return filtered_events

def get_events_definition_from_contract(contract_address):
    abi = json.loads(get_contract_info(contract_address)['abi'])
    events_abi = list(filter(lambda x: x['type'] == "event", abi))
    return [dict(event, **{'keys': [get_selector_from_name(event['name'])]}) for event in events_abi]

def get_event_structure_from_abi(abi, event_name):
    return list(filter(lambda x: x['type'] == "event" and x['name'] == event_name, abi))

class BlockEventsParser:
    def __init__(self, events) -> None:
        self.raw_events = events
        self.initialize()

    def initialize(self):
        involved_contracts = set([event['from_address'] for event in self.raw_events])
        self.involved_contracts_events = {contract_address: get_events_definition_from_contract(contract_address) for contract_address in involved_contracts}
        for event in self.raw_events:
            involved_contract_event_definition = list(filter(lambda x: x['keys'] == event['keys'], self.involved_contracts_info[event['from_address']]))[0]
            event['name'] = involved_contract_event_definition['name']
            event['transformed_data'] = EventData(event['data'], involved_contract_event_definition['data'])

class EventData:
    def __init__(self, event_data, structure) -> None:
        self.raw_event_data = event_data
        self.event_data = []
        self.structure = structure

    def initialize(self):
        for offset, struct in enumerate(self.structure):
            self.raw_event_data = self.raw_event_data[1:]
            current_value = {
                "name": struct['name'],
                "type": struct['type'],
                "value": self.raw_event_data
            }
            self.event_data.append(current_value)
