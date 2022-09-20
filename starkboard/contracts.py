import json
import gzip
import base64
import asyncio
from datetime import datetime
from starkboard.tokens import insert_token_info
from starkboard.constants import LIST_EVENT_KEYS, CONTRACT_STANDARDS, APP_NAME
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.contract import Contract
from starkboard.utils import decimal_to_hex


def count_contract_deployed_current_block(starknet_node, starknet_gateway):
    """
    Retrieve the number of deployed contracts on StarkNet
    """
    r = starknet_node.post("", method="starknet_blockNumber", params=[])
    block_number = json.loads(r.text)["result"]  
    transactions = json.loads(starknet_gateway.get(f"get_block?blockNumber={block_number}").text)
    deploy_tx = [tx for tx in transactions["transactions"] if tx["type"] == "DEPLOY"]
    return {
        "countDeployedContract": len(deploy_tx)
    }


def count_contract_deployed_in_block(block_txs):
    """
    Retrieve the number of deployed contracts on StarkNet
    """
    deploy_tx = [tx for tx in block_txs if tx["type"] == "DEPLOY"]
    return {
        "count_deployed_contracts": len(deploy_tx)
    }


def most_used_functions_from_contract(block_txs):
    """
    Retrieve the number of deployed contracts on StarkNet
    @TODO
    """
    deploy_tx = [tx for tx in block_txs if tx["type"] == "DEPLOY"]
    return None

def get_declared_class_in_block(block_txs, node, db):
    """
    Retrieve the list of transactions hash from a given block number
    """
    declared_hashes = [tx.get('class_hash') for tx in block_txs if tx["type"] == "DECLARE"]
    for declared_contract in declared_hashes:
        prog = get_class_program(declared_contract, node)
        base64_bytes = prog.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        json_code = json.loads(gzip.decompress(message_bytes).decode()).get('identifiers')
        event_names = [key.split('.')[-2] for key in list(json_code) if "emit_event" in key and not "syscalls.emit_event" in key]
        event_full_names = [key for key in list(json_code) if key.endswith(".emit") and "__main__" not in key.split('.')[-2] and not "syscalls.emit_event" in key]
        abi_keys = []
        abi = []
        for k in event_full_names:
            event_data = dict(sorted(json_code[f'{k}.Args']['members'].items(), key=lambda item: item[1].get('offset')))
            abi_event_data = [{"name": arg, "type": event_data[arg].get('cairo_type').split('.')[-1]} for arg in event_data]
            abi_part = {
                "data": abi_event_data,
                "name": k.split('.')[-2],
                "keys": [],
                "type": "event"
            }
            abi.append(abi_part)
            for ev_d in event_data:
                struct_name = event_data[ev_d].get('cairo_type')
                if struct_name[-1] == "*":
                    struct_name = struct_name[:-1]
                if struct_name != "felt" and struct_name != "felt*":
                    struct_data = json_code[struct_name]
                    composition = dict(sorted(struct_data['members'].items(), key=lambda item: item[1].get('offset')))
                    abi_struct_data = [{
                        "name": arg, 
                        "type": composition[arg].get('cairo_type').split('.')[-1],
                        "offset": composition[arg].get('offset')
                    } for arg in composition]
                    abi_part = {
                        "name": struct_data['full_name'].split('.')[-1],
                        "members": abi_struct_data,
                        "size":  struct_data['size'],
                        "type": struct_data['type']
                    }
                    abi.append(abi_part)
        for k, v in json_code.items():
            if '__main__' in k and v.get('decorators') and any(decorator in ["external", "view", "constructor", "l1_handler"] for decorator in v.get('decorators')):
                abi_keys.append((k, v.get('decorators'), None))
            elif '__main__' in k and v.get('destination') and any(decorator in ["external", "view"] for decorator in json_code.get(v.get('destination'), {}).get('decorators', {})):
                abi_keys.append((k, json_code.get(v.get('destination')).get('decorators'), v.get('destination')))
        for (k, decorators, dest) in abi_keys:
            if dest:
                inputs = json_code[f'{dest}.Args'].get('members')
                inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
                for member, member_type in inputs.items()]
                if json_code[f'{dest}.Return'].get('cairo_type'):
                    outputs = [json_code[f'{dest}.Return']['cairo_type'][1:len(json_code[f'{dest}.Return']['cairo_type'])-1]]
                else:
                    outputs = []
                if outputs == ['']:
                    outputs = []
                else:
                    outputs = [{"name": v.split(':')[0].replace(' ', ''), "type": v.split(':')[1].split('.')[-1]} for v in outputs]
                abi_part = {
                    "inputs": inputs,
                    "name": k.split('.')[-1],
                    "outputs": outputs,
                    "type": "function"
                }            
            else:
                inputs = json_code[f'{k}.Args'].get('members')
                inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
                for member, member_type in inputs.items()]
                if json_code[f'{k}.Return'].get('cairo_type'):
                    outputs = [json_code[f'{k}.Return']['cairo_type'][1:len(json_code[f'{k}.Return']['cairo_type'])-1]]
                else:
                    outputs = []
                if outputs == ['']:
                    outputs = []
                else:
                    outputs = [{"name": v.split(':')[0].replace(' ', ''), "type": v.split(':')[1].split('.')[-1]} for v in outputs]
                if "constructor" in json_code[k].get('decorators'):
                    function_type = "constructor"
                elif "l1_handler" in json_code[k].get('decorators'):
                    function_type = "l1_handler"
                else:
                    function_type = "function"
                abi_part = {
                    "inputs": inputs,
                    "name": k.split('.')[-1],
                    "outputs": outputs,
                    "type": function_type
                }
            if "view" in decorators:
                abi_part["stateMutability"] = "view"
            abi.append(abi_part)
        event_keys = [LIST_EVENT_KEYS.get(event_name) for event_name in event_names if LIST_EVENT_KEYS.get(event_name)]
        class_type = get_contract_class_type(abi_keys, event_names)
        if not class_type:
            class_type = "UNKNOWN"
        class_object = {
            'class_hash': declared_contract,
            'abi': json.dumps(abi),
            'event_names': json.dumps(event_names),
            'event_keys': json.dumps(event_keys),
            'type': class_type
        }
        db.insert_contract_hash(class_object)

def get_declared_class(class_hash, node, db):
    prog = get_class_program(class_hash, node)
    base64_bytes = prog.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    json_code = json.loads(gzip.decompress(message_bytes).decode()).get('identifiers')
    event_names = [key.split('.')[-2] for key in list(json_code) if key.endswith(".emit_event") and "__main__" not in key.split('.')[-2] and not "syscalls.emit_event" in key]
    event_full_names = [key for key in list(json_code) if key.endswith(".emit") and "__main__" not in key.split('.')[-2] and not "syscalls.emit_event" in key]
    abi_keys = []
    abi = []
    for k in event_full_names:
        event_data = dict(sorted(json_code[f'{k}.Args']['members'].items(), key=lambda item: item[1].get('offset')))
        abi_event_data = [{"name": arg, "type": event_data[arg].get('cairo_type').split('.')[-1]} for arg in event_data]
        abi_part = {
            "data": abi_event_data,
            "name": k.split('.')[-2],
            "keys": [],
            "type": "event"
        }
        abi.append(abi_part)
        for ev_d in event_data:
            struct_name = event_data[ev_d].get('cairo_type')
            if struct_name[-1] == "*":
                struct_name = struct_name[:-1]
            if struct_name != "felt" and struct_name != "felt*":
                struct_data = json_code[struct_name]
                composition = dict(sorted(struct_data['members'].items(), key=lambda item: item[1].get('offset')))
                abi_struct_data = [{
                    "name": arg, 
                    "type": composition[arg].get('cairo_type').split('.')[-1],
                    "offset": composition[arg].get('offset')
                } for arg in composition]
                abi_part = {
                    "name": struct_data['full_name'].split('.')[-1],
                    "members": abi_struct_data,
                    "size":  struct_data['size'],
                    "type": struct_data['type']
                }
                abi.append(abi_part)
    for k, v in json_code.items():
        if '__main__' in k and v.get('decorators') and any(decorator in ["external", "view", "constructor", "l1_handler"] for decorator in v.get('decorators')):
            abi_keys.append((k, v.get('decorators'), None))
        elif '__main__' in k and v.get('destination') and any(decorator in ["external", "view"] for decorator in json_code.get(v.get('destination'), {}).get('decorators', {})):
            abi_keys.append((k, json_code.get(v.get('destination')).get('decorators'), v.get('destination')))
    for (k, decorators, dest) in abi_keys:
        if dest:
            inputs = json_code[f'{dest}.Args'].get('members')
            inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
            for member, member_type in inputs.items()]
            if json_code[f'{dest}.Return'].get('cairo_type'):
                outputs = [json_code[f'{dest}.Return']['cairo_type'][1:len(json_code[f'{dest}.Return']['cairo_type'])-1]]
            else:
                outputs = []
            if outputs == ['']:
                outputs = []
            else:
                outputs = [{"name": v.split(':')[0].replace(' ', ''), "type": v.split(':')[1].split('.')[-1]} for v in outputs]
            abi_part = {
                "inputs": inputs,
                "name": k.split('.')[-1],
                "outputs": outputs,
                "type": "function"
            }            
        else:
            inputs = json_code[f'{k}.Args'].get('members')
            inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
            for member, member_type in inputs.items()]
            if json_code[f'{k}.Return'].get('cairo_type'):
                outputs = [json_code[f'{k}.Return']['cairo_type'][1:len(json_code[f'{k}.Return']['cairo_type'])-1]]
            else:
                outputs = []
            if outputs == ['']:
                outputs = []
            else:
                outputs = [{"name": v.split(':')[0].replace(' ', ''), "type": v.split(':')[1].split('.')[-1]} for v in outputs]
            if "constructor" in json_code[k].get('decorators'):
                function_type = "constructor"
            elif "l1_handler" in json_code[k].get('decorators'):
                function_type = "l1_handler"
            else:
                function_type = "function"
            abi_part = {
                "inputs": inputs,
                "name": k.split('.')[-1],
                "outputs": outputs,
                "type": function_type
            }
        if "view" in decorators:
            abi_part["stateMutability"] = "view"
        abi.append(abi_part)
    event_keys = [LIST_EVENT_KEYS.get(event_name) for event_name in event_names if LIST_EVENT_KEYS.get(event_name)]
    class_type = get_contract_class_type(abi_keys, event_names)
    if not class_type:
        class_type = "UNKNOWN"
    class_object = {
        'class_hash': class_hash,
        'abi': json.dumps(abi),
        'event_names': json.dumps(event_names),
        'event_keys': json.dumps(event_keys),
        'type': class_type
    }
    db.insert_contract_hash(class_object)
    return class_object

def get_class_program(class_hash, starknet_node=None):
    """
    Retrieve the program gzip encoded of a given class
    """
    params = class_hash
    r = starknet_node.post("", method="starknet_getClass", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]['program']

def get_class_abi(class_hash, starknet_sequencer=None):
    """
    Retrieve the ABI of a given class
    """
    r = starknet_sequencer.get(f'get_class_by_hash?classHash={class_hash}')
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data['abi']

def get_contract_class_type(abi_keys, event_names):
    list_functions = list(map(lambda x: x[0].split('.')[-1], abi_keys))
    for typed in CONTRACT_STANDARDS:
        if all(a in event_names for a in typed["event_names"]) and all(a in list_functions for a in typed["functions"]):
            return typed["name"]
    return None

def get_class_info(class_hash, starknet_node, db):
    class_info = db.get_contract_hash(class_hash)
    if not class_info:
        class_info = get_declared_class(class_hash, starknet_node, db)
    return class_info

async def insert_contract_info(contract_address, starknet_node, db, class_hash=None):
    if not class_hash:
        params = contract_address
        r = starknet_node.post("", method="starknet_getClassHashAt", params=["pending", params])
        data = json.loads(r.text)
        if 'error'in data:
            return data['error']
        class_hash = data['result']
    contract_class = get_class_info(class_hash, starknet_node, db)
    contract_class = get_class_info(class_hash, starknet_node, db)
    if contract_class:
        if contract_class.get('type') == "Proxy":
            proxy_contract = await get_proxy_contract(contract_address, contract_class.get("abi"), starknet_node, db)
            abi = proxy_contract.get("abi", "[]")
            event_keys = proxy_contract.get("event_keys", "[]")
            contract_type = proxy_contract.get('type')
        else:
            abi = contract_class.get("abi", "[]")
            event_keys = contract_class.get("event_keys", "[]")
            contract_type = contract_class.get('type')
    newly_contract_found = {
        "contract_address": contract_address,
        "application": "Unknown",
        "event_keys": event_keys,
        "abi": abi,
        "class_hash": class_hash,
        "type": contract_type,
        "deployed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    db.insert_contract(newly_contract_found)
    return newly_contract_found

async def get_contract_info(contract_address, starknet_node, db, class_hash=None):
    contract_info = db.get_contract(contract_address)
    if not contract_info:
        contract_info = await insert_contract_info(contract_address, starknet_node, db, class_hash)
    return contract_info

async def get_pool_info(contract_address, starknet_node, db):
    try:
        client = FullNodeClient(starknet_node.base_url, db.network)
        contract_info = await get_contract_info(contract_address, starknet_node, db)
        print("get contract of pool")
        if contract_info.get('view_info'):
            view_info = json.loads(contract_info.get('view_info'))
            token0_address = view_info.get('token0')
            token1_address = view_info.get('token1')
        else:
            contract = Contract(address=int(contract_address, 16), abi=json.loads(contract_info.get('abi')), client=client)
            token0_address, token1_address = await get_pool_tokens(contract, db)
        token0 = await get_contract_info(token0_address, starknet_node, db)
        token1 = get_contract_info(token1_address, starknet_node, db)
        if token0.get('view_info'):
            token0_info = json.loads(token0.get('view_info'))
        else:
            token0_info = await insert_token_info(token0_address, client, db)
        if token1.get('view_info'):
            token1_info = json.loads(token1.get('view_info'))
        else:
            token1_info = await insert_token_info(token1_address, client, db)
        pool_info = {
            "token0": token0_address,
            "token0_info": token0_info,
            "token1": token1_address,
            "token1_info": token1_info,
            "abi": json.loads(contract_info.get('abi'))
        }
        return pool_info
    except:
        print(f'Contract {contract_address} is not at Standard.')
        return {}

async def get_pool_tokens(contract, db):
    (name,) = await contract.functions["name"].call()
    (symbol,) = await contract.functions["symbol"].call()
    (decimals,) = await contract.functions["decimals"].call()
    token0_handler = list(filter(lambda function_key: "token0" in function_key.lower(), contract.functions))[0]
    token1_handler = list(filter(lambda function_key: "token1" in function_key.lower(), contract.functions))[0]
    (token0_address,) = await contract.functions[token0_handler].call()
    (token1_address,) = await contract.functions[token1_handler].call()
    token0_address = decimal_to_hex(token0_address)
    token1_address = decimal_to_hex(token1_address)
    data = {
        "contract_address": decimal_to_hex(contract.address),
        "view_info": {
            "name": bytearray.fromhex(hex(name)[2:]).decode(),
            "symbol": bytearray.fromhex(hex(symbol)[2:]).decode(),
            "decimals": decimals,
            "token0": token0_address,
            "token1": token1_address
        }
    }
    db.insert_contract_view_info(data)
    return token0_address, token1_address

async def call_implementation(contract, node, db):
    (contract_implementation,) = await contract.functions["get_implementation"].call()
    contract_implementation = decimal_to_hex(contract_implementation)
    try:
        contract_info = get_class_info(contract_implementation, node, db)
    except:
        contract_info = await get_contract_info(contract_implementation, node, db)
    return contract_info

async def get_proxy_contract(contract_address, proxy_abi, node, db):
    try:
        client = FullNodeClient(node.base_url, db.network)
        contract = Contract(address=int(contract_address, 16), abi=json.loads(proxy_abi), client=client)
        contract_info = await call_implementation(contract, node, db)
        return contract_info
    except Exception as e:
        print(f'Contract {contract_address} is not at Standard.')
        return {}
