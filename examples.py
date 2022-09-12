import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.ecosystem.fetch_application import update_core_ecosystem
from starkboard.transactions import transactions_in_block, state_update
from starkboard.contracts import class_hashes, get_class_program, classify_hash_contract
import base64
import gzip
import json
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    for block in range(320000, 330000):
        current_block = state_update(block, starknet_node=staknet_node)
        deploy_txs = current_block.get('deployed_contracts')
        hashes = list(map(lambda x: x['class_hash'], deploy_txs))
        #print(current_block['declared_contracts'])
        list_unwanted_hash = list(map(lambda x: x['hash'], filter(lambda x: x['type'] == "wallet" or x['type'] == "starkware", class_hashes)))
        deploy_txs = [tx for tx in deploy_txs if tx.get('class_hash') not in list_unwanted_hash]
        if deploy_txs:
            list_class_hash = set([tx.get('class_hash') for tx in deploy_txs])
            for class_hash in list_class_hash:
                prog = get_class_program(class_hash, staknet_node)
                base64_bytes = prog.encode('utf-8')
                message_bytes = base64.b64decode(base64_bytes)
                json_code = json.loads(gzip.decompress(message_bytes).decode()).get('identifiers')
                main_functions = list(filter(lambda x: '__main__' in x, list(json_code.keys())))
                final_functions = list(set(list(map(lambda x: x.split('.')[1], main_functions))))
                classify_hash_contract(class_hash, final_functions)
