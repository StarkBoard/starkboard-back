import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.constants import EVENT_KEYS_RETAINER
from starkboard.events.events import get_events
from starkboard.fees import get_fees_in_block
from starkboard.tokens import insert_token_info
from starkboard.transactions import transactions_in_block
from starkboard.contracts import get_declared_class_in_block, get_declared_class, get_proxy_contract
from starkboard.ecosystem.auth import get_starknet_ecosystem_db_token
from monitor import monitor_deployed_contracts
from starknet_py.net.full_node_client import FullNodeClient
from starkboard.events.events import BlockEventsParser
import asyncio
import argparse
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--contract", help="Contract to Filter On", required=False)

async def fetch_contract_info():
    list_erc20 = [
    ]
    for erc20 in list_erc20:
        print(erc20)
        client = FullNodeClient(starknet_node.base_url, db.network)
        res = await insert_token_info(erc20, client, db)
        print(res)
    return None




if __name__ == '__main__':

    args = parser.parse_args()
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    staknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    loop = asyncio.get_event_loop()
    auth = get_starknet_ecosystem_db_token()
    




    #x = get_declared_class("0x5a6caca1dcfb2af22d831e678b544e6aa24056a4c35476a8cbbdd8a6ab1f3eb", starknet_node, db)
    #print(x['abi'])
    #loop.run_until_complete(fetch_contract_info())
    """
    for block in range(340719, 345000):#347613
        events = get_events(block, starknet_node=starknet_node)
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        fees = get_fees_in_block(block_transactions['transactions'], starknet_node=starknet_node)
        #Oracle Publishers
        if args.contract:
            events = list(filter(lambda x: int(x['from_address'], 16) == int(args.contract, 16), events))
        events = list(filter(lambda x: x['keys'][0] in EVENT_KEYS_RETAINER, events))
        if events:
            print('')
            print('#####################################################################################')
            print(f'#                                     [BLOCK {block}]                                #')
            print('#####################################################################################')
            block_events_parser = BlockEventsParser(events, block_transactions['timestamp'], fees['fee_per_tx'], starknet_node, db, loop)
            formatted_events = list(filter(lambda x: x['event_key'] in EVENT_KEYS_RETAINER, block_events_parser.events))
            db.insert_events_bulk(formatted_events)
            print('')
        #monitor_deployed_contracts(block_transactions['transactions'], block_transactions['timestamp'], starknet_node, db)
        #declared_tx = [tx for tx in block_transactions['transactions'] if tx["type"] == "DECLARE"]
        #if declared_tx:
        #    print(f'Declared a contract at block {block}')
        #    get_declared_class_in_block(declared_tx, starknet_node, db)
    """
