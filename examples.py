import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.events.events import get_events
from starkboard.transactions import transactions_in_block, get_swap_info_in_block
from starkboard.contracts import get_declared_class_in_block, get_declared_class
from monitor import monitor_deployed_contracts
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    staknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    loop = asyncio.get_event_loop()
    """
    contract_classes = db.get_all_contract_hash()
    for contract_class in contract_classes:
        if contract_class.get('network') == "testnet":
            print(f'getting class hash : {contract_class.get("class_hash")}')
            get_declared_class(contract_class.get('class_hash'), starknet_node, db)
        else:
            print(f'getting class hash : {contract_class.get("class_hash")}')
            get_declared_class(contract_class.get('class_hash'), starknet_node_mainnet, db_mainnet)
    """
    for block in range(310000, 320000):
        #events = get_events(block, starknet_node=starknet_node)
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        #get_swap_info_in_block(block_transactions['timestamp'], events, starknet_node, db, loop)
        #monitor_deployed_contracts(block_transactions['transactions'], block_transactions['timestamp'], starknet_node, db)
        declared_tx = [tx for tx in block_transactions['transactions'] if tx["type"] == "DECLARE"]
        if declared_tx:
            print(f'Declared a contract at block {block}')
            get_declared_class_in_block(declared_tx, starknet_node, db)
