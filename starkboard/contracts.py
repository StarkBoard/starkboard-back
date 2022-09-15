import json
import gzip
import base64
from starkboard.constants import LIST_EVENT_KEYS, EVENT_KEYS, CLASS_HASH_TYPE, APP_NAME


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
        main_functions = list(filter(lambda x: '__main__' in x, list(json_code.keys())))
        final_functions = set(list(map(lambda x: x.split('.')[1], main_functions)))
        event_names = [key.split('.')[-2] for key in list(json_code) if "emit_event" in key and not "syscalls.emit_event" in key]
        abi_keys = [(k, v.get('decorators')) for k, v in json_code.items() if "__main__" in k and v.get('decorators') and any(decorator in ["external", "view"] for decorator in v.get('decorators'))]
        abi = []
        for (k, decorators) in abi_keys:
            inputs = json_code[f'{k}.Args'].get('members')
            inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
            for member, member_type in inputs.items()]
            if json_code[f'{k}.Return'].get('cairo_type'):
                outputs = json_code[f'{k}.Return']['cairo_type'][1:len(json_code[f'{k}.Return']['cairo_type'])-1]
            else:
                outputs = []
            if outputs:
                outputs = []
            else:
                outputs = [{"name": v.split(':')[0], "type": v.split(':')[1].split('.')[-1]} for v in outputs]
            abi_part = {
                "inputs": inputs,
                "name": k.split('.')[-1],
                "outputs": outputs,
                "type": "function"
            }
            if "view" in decorators:
                abi_part["stateMutability"] = "view"
            abi.append(abi_part)
        event_keys = [LIST_EVENT_KEYS.get(event_name) for event_name in event_names if LIST_EVENT_KEYS.get(event_name)]
        class_type = get_contract_class_type(final_functions)
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
    main_functions = list(filter(lambda x: '__main__' in x, list(json_code.keys())))
    final_functions = set(list(map(lambda x: x.split('.')[1], main_functions)))
    event_names = [key.split('.')[-2] for key in list(json_code) if "emit_event" in key and not "syscalls.emit_event" in key]
    abi_keys = [(k, v.get('decorators')) for k, v in json_code.items() if "__main__" in k and v.get('decorators') and any(decorator in ["external", "view"] for decorator in v.get('decorators'))]
    abi = []
    for (k, decorators) in abi_keys:
        inputs = json_code[f'{k}.Args'].get('members')
        inputs = [{"name": member, "type": member_type['cairo_type'].split('.')[-1]} 
        for member, member_type in inputs.items()]
        if json_code[f'{k}.Return'].get('cairo_type'):
            outputs = json_code[f'{k}.Return']['cairo_type'][1:len(json_code[f'{k}.Return']['cairo_type'])-1]
        else:
            outputs = []
        if outputs:
            outputs = []
        else:
            outputs = [{"name": v.split(':')[0], "type": v.split(':')[1].split('.')[-1]} for v in outputs]
        abi_part = {
            "inputs": inputs,
            "name": k.split('.')[-1],
            "outputs": outputs,
            "type": "function"
        }
        if "view" in decorators:
            abi_part["stateMutability"] = "view"
        abi.append(abi_part)
    event_keys = [LIST_EVENT_KEYS.get(event_name) for event_name in event_names if LIST_EVENT_KEYS.get(event_name)]
    class_type = get_contract_class_type(final_functions)
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
    Retrieve the list of transactions hash from a given block number
    """
    params = class_hash
    r = starknet_node.post("", method="starknet_getClass", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    return data["result"]['program']

def get_contract_class_type(list_functions):
    for typed in EVENT_KEYS:
        if all(a in list_functions for a in typed[0]):
            return typed[1]
    return None

def get_class_type(list_functions):
    for typed in EVENT_KEYS:
        if all(a in list_functions for a in typed[0]):
            return typed[1], typed[2]
    return None, None

def get_hash_contract_info(type):
    event_keys = CLASS_HASH_TYPE[type][2]
    if type == "ERC20-LP":
        return type, event_keys+LIST_EVENT_KEYS["Swap"]
    else:
        return type, event_keys

def get_application_name(type):
    return APP_NAME.get(type, "Unknown")

def index_deployed_contract(db):
    return {}
