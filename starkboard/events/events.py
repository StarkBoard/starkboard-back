import json
from starkware.starknet.compiler.compile import get_selector_from_name

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

def get_events_from_abi(abi):
    return list(filter(lambda x: x['type'] == "event", abi))

def get_event_structure_from_abi(abi, event_name):
    return list(filter(lambda x: x['type'] == "event" and x['name'] == event_name, abi))

class BlockEventsParser:
    def __init__(self, events) -> None:
        self.raw_events = events
        
