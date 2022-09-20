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

def get_events_definition_from_contract(contract_address, starknet_node, db):
    abi = json.loads(get_contract_info(contract_address, starknet_node, db)['abi'])
    events_abi = list(filter(lambda x: x['type'] == "event", abi))
    struct_abi = list(filter(lambda x: x['type'] == "struct", abi))
    return [dict(event, **{'keys': [get_selector_from_name(event['name'])]}) for event in events_abi], struct_abi

def get_event_structure_from_abi(abi, event_name):
    return list(filter(lambda x: x['type'] == "event" and x['name'] == event_name, abi))

def get_struct(structs, name):
    return list(filter(lambda x: x['name'] == name, structs))[0]

class BlockEventsParser:

    def __init__(self, events, starknet_node, db) -> None:
        self.starknet_node = starknet_node
        self.db = db
        self.raw_events = events
        self.initialize()

    def initialize(self):
        involved_contracts = set([event['from_address'] for event in self.raw_events])
        self.involved_contracts_events = {contract_address: get_events_definition_from_contract(contract_address, self.starknet_node, self.db) for contract_address in involved_contracts}
        for event in self.raw_events:
            print(f'   > Involed Contract : {event["from_address"]} for a {event["keys"]} Event.')
            involved_contract_events, involved_contract_structs = self.involved_contracts_events[event['from_address']]
            involved_contract_event_definition = list(filter(lambda x: x['keys'][0] == int(event['keys'][0], 16), involved_contract_events))[0]
            event['name'] = involved_contract_event_definition['name']
            event['transformed_data'] = EventData(event['data'], involved_contract_event_definition['data'], involved_contract_structs)

class EventData:

    def __init__(self, event_data, members, structs) -> None:
        self.raw_event_data = event_data
        self.event_data = []
        self.members = members
        self.structs = structs
        self.transformed_data = []
        self.initialize()

    def initialize(self):
        for index, member in enumerate(self.members):
            member_type = member['type']
            if len(self.members) > index+1 and self.members[index]['type'] == "felt*":
                continue
            if member['type'] == "felt":
                value = self.raw_event_data[:1][0]
                self.raw_event_data = self.raw_event_data[1:]
            elif member['type'].endswith('*'):
                value = self.raw_event_data[:self.members[index-1]]
                self.raw_event_data = self.raw_event_data[self.members[index-1]:]
            else:
                value = self.build_member_value(member)
            member_value = {
                "name": member['name'],
                "type": member_type,
                "value": value
            }
            self.transformed_data.append(member_value)
        print(self.transformed_data)

    def build_member_value(self, member):
        current_struct = get_struct(self.structs, member['type'])
        struct_val = {}
        for index, struct_member in enumerate(current_struct['members']):
            if len(current_struct['members']) > index+1 and current_struct['members'][index]['type'] == "felt*":
                continue
            if struct_member['type'] == "felt":
                val = self.raw_event_data[:1][0]
                self.raw_event_data = self.raw_event_data[1:]
                struct_val[struct_member['name']] = val
            elif struct_member['type'].endswith('*'):
                val = self.raw_event_data[:current_struct['members'][index-1]]
                self.raw_event_data = self.raw_event_data[current_struct['members'][index-1]:]
                struct_val[struct_member['name']] = val
            else:
                struct_val[struct_member['name']] = self.build_member_value(struct_member)
        return struct_val
