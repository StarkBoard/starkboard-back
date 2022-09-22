import json
import asyncio
from datetime import datetime
from starkware.starknet.compiler.compile import get_selector_from_name
from starkboard.contracts import get_contract_info
from starkboard.events.normalizer import EventNormalizer

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

async def get_events_definition_from_contract(contract_address, starknet_node, db):
    contract_info = await get_contract_info(contract_address, starknet_node, db)
    abi = json.loads(contract_info['abi'])
    events_abi = list(filter(lambda x: x['type'] == "event", abi))
    struct_abi = list(filter(lambda x: x['type'] == "struct", abi))
    return [dict(event, **{'keys': [get_selector_from_name(event['name'])]}) for event in events_abi], struct_abi

def get_event_structure_from_abi(abi, event_name):
    return list(filter(lambda x: x['type'] == "event" and x['name'] == event_name, abi))

def get_struct(structs, name):
    return list(filter(lambda x: x['name'] == name, structs))[0]

class BlockEventsParser:

    def __init__(self, events, timestamp, fees_per_tx, starknet_node, db, loop) -> None:
        self.starknet_node = starknet_node
        self.fees_per_tx = fees_per_tx
        self.timestamp = timestamp
        self.db = db
        self.raw_events = events
        self.events = []
        self.involved_contracts_events = {}
        self.loop = loop
        self.initialize()

    def initialize(self):
        involved_contracts = set([event['from_address'] for event in self.raw_events])
        group = asyncio.gather(*[get_events_definition_from_contract(contract_address, self.starknet_node, self.db) for contract_address in involved_contracts])
        results = self.loop.run_until_complete(group)
        for idx, contract in enumerate(involved_contracts):
            self.involved_contracts_events[contract] = results[idx]
        for raw_event in self.raw_events:
            try:
                event = {}
                involved_contract_events, involved_contract_structs = self.involved_contracts_events[raw_event['from_address']]
                involved_contract_event_definition = list(filter(lambda x: x['keys'][0] == int(raw_event['keys'][0], 16), involved_contract_events))[0]
                event['event_name'] = involved_contract_event_definition['name']
                event['contract_address'] = raw_event["from_address"]
                event['block_number'] = raw_event["block_number"]
                event['tx_hash'] = raw_event["transaction_hash"]
                event['event_key'] = raw_event['keys'][0]
                event['timestamp'] = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                event['full_day'] = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')
                event['total_fees'] = self.fees_per_tx[raw_event['transaction_hash']]
                event['data'] = json.dumps(EventData(event['event_name'], raw_event['data'], involved_contract_event_definition['data'], involved_contract_structs).event_data)
                print(f'🎟️ Contract {event["contract_address"]}  emitted a {event["event_name"]} Event')
                self.events.append(event)
            except Exception as e:
                print(e)
                print(f'❌ Error while parsing event {raw_event["keys"]} of Contract {raw_event["from_address"]}')

class EventData:

    def __init__(self, event_name, event_data, members, structs) -> None:
        self.event_name = event_name
        self.raw_event_data = event_data
        self.event_data = []
        self.members = members
        self.structs = structs
        self.initialize()

    def initialize(self):
        for index, member in enumerate(self.members):
            member_type = member['type']
            if len(self.members) > index+1 and self.members[index+1]['type'].endswith('*'):
                continue
            if member['type'].endswith('*') and int(self.raw_event_data[0], 16) == 0:
                value = []
                self.raw_event_data = self.raw_event_data[1:]
            elif member['type'] == "felt":
                value = self.raw_event_data[:1][0]
                self.raw_event_data = self.raw_event_data[1:]
            elif member['type'] == "felt*":
                length = int(self.raw_event_data[0], 16)
                value = self.raw_event_data[1:length+1]
                self.raw_event_data = self.raw_event_data[length+1:]
            elif member['type'].endswith('*'):
                object_length = int(self.raw_event_data[0], 16)
                self.raw_event_data = self.raw_event_data[1:]
                value = [self.build_member_value(member) for i in range(object_length)]
            else:
                value = self.build_member_value(member)
            member_value = {
                "name": member['name'],
                "type": member_type,
                "value": value
            }
            self.event_data.append(member_value)
        self.event_data = EventNormalizer(self.event_name, self.event_data).get_normalized_event()

    def build_member_value(self, member):
        current_struct = get_struct(self.structs, member['type'])
        struct_val = {}
        for index, struct_member in enumerate(current_struct['members']):
            if len(current_struct['members']) > index+1 and current_struct['members'][index+1]['type'].endswith('*'):
                continue
            elif struct_member['type'].endswith('*') and int(self.raw_event_data[0], 16) == 0:
                struct_val[struct_member['name']] = []
                self.raw_event_data = self.raw_event_data[1:]
            if struct_member['type'] == "felt":
                val = self.raw_event_data[:1][0]
                self.raw_event_data = self.raw_event_data[1:]
                struct_val[struct_member['name']] = val
            elif struct_member['type'] == "felt*":
                length = int(self.raw_event_data[0], 16)
                val = self.raw_event_data[1:length+1]
                self.raw_event_data = self.raw_event_data[length+1:]
                struct_val[struct_member['name']] = val
            elif struct_member['type'].endswith('*'):
                object_length = int(self.raw_event_data[0], 16)
                self.raw_event_data = self.raw_event_data[1:]
                struct_val[struct_member['name']] = [self.build_member_value(member) for i in range(object_length)]
            else:
                struct_val[struct_member['name']] = self.build_member_value(struct_member)
        return struct_val
