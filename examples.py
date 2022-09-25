import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.constants import EVENT_KEYS_RETAINER
from starkboard.events.events import get_events
from starkboard.fees import get_fees_in_block
from starkboard.tokens import insert_token_info
from starkboard.transactions import transactions_in_block, get_swap_info_in_block
from starkboard.contracts import get_declared_class_in_block, get_declared_class, get_proxy_contract
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
    list_erc20 = ["0x03fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac",
        "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
        "0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8",
        "0x22b05f9396d2c48183f6deaf138a57522bcc8b35b67dee919f76403d1783136",
        "0x25b392609604c75d62dde3d6ae98e124a31b49123b8366d7ce0066ccb94f696",
        "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
        "0x53c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
        "0x5528ddad13a21aa2447f51bc6b7fdbe1882700ea94b2b2b955a27f13e00571f",
        "0x7c662b10f409d7a0a69c8da79b397fd91187ca5f6230ed30effef2dceddc5b3",
        "0xda114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3",
        "0xda1eb497a6cf27aade692d7f502e514ca761f15a29e24a3ffc3ace8832fb91"
    ]
    for erc20 in list_erc20:
        print(erc20)
        client = FullNodeClient(starknet_node.base_url, db.network)
        res = await insert_token_info(erc20, client, db)
        print(res)
    return None

if __name__ == '__main__':

    args = parser.parse_args()
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
    staknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("mainnet")
    loop = asyncio.get_event_loop()
    #x = get_declared_class("0x5a6caca1dcfb2af22d831e678b544e6aa24056a4c35476a8cbbdd8a6ab1f3eb", starknet_node, db)
    #print(x['abi'])
    loop.run_until_complete(fetch_contract_info())
    """
    for block in range(4425, 5000):#343056    5241
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
        #get_swap_info_in_block(block_transactions['timestamp'], events, starknet_node, db, loop)
        #monitor_deployed_contracts(block_transactions['transactions'], block_transactions['timestamp'], starknet_node, db)
        #declared_tx = [tx for tx in block_transactions['transactions'] if tx["type"] == "DECLARE"]
        #if declared_tx:
        #    print(f'Declared a contract at block {block}')
        #    get_declared_class_in_block(declared_tx, starknet_node, db)
    """