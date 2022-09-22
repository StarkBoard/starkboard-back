import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.constants import EVENT_KEYS_RETAINER
from starkboard.events.events import get_events
from starkboard.fees import get_fees_in_block
from starkboard.transactions import transactions_in_block, get_swap_info_in_block
from starkboard.contracts import get_declared_class_in_block, get_declared_class, get_proxy_contract
from monitor import monitor_deployed_contracts
from starkboard.events.events import BlockEventsParser
import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--contract", help="Contract to Filter On", required=False)
#0x749e31eee7101051df8d3e4f9d653d78c44392f8dd86a4ddfa8833ce5945c35

if __name__ == '__main__':

    args = parser.parse_args()
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    staknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    loop = asyncio.get_event_loop()
    #x = get_declared_class("0x5a6caca1dcfb2af22d831e678b544e6aa24056a4c35476a8cbbdd8a6ab1f3eb", starknet_node, db)
    #print(x['abi'])
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
    for block in range(344040, 350000):#343056    5082
        events = get_events(block, starknet_node=starknet_node)
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        fees = get_fees_in_block(block_transactions['transactions'], starknet_node=starknet_node)
        events = list(filter(lambda x: x['keys'] in EVENT_KEYS_RETAINER, events))
        #Oracle Publishers
        if args.contract:
            events = list(filter(lambda x: int(x['from_address'], 16) == int(args.contract, 16), events))
        if events:
            print('')
            print('#####################################################################################')
            print(f'#                                     [BLOCK {block}]                                #')
            print('#####################################################################################')
            block_events = BlockEventsParser(events, block_transactions['timestamp'], fees['fee_per_tx'], starknet_node, db, loop)
            print('')
        #get_swap_info_in_block(block_transactions['timestamp'], events, starknet_node, db, loop)
        #monitor_deployed_contracts(block_transactions['transactions'], block_transactions['timestamp'], starknet_node, db)
        #declared_tx = [tx for tx in block_transactions['transactions'] if tx["type"] == "DECLARE"]
        #if declared_tx:
        #    print(f'Declared a contract at block {block}')
        #    get_declared_class_in_block(declared_tx, starknet_node, db)
