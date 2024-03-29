import os
import argparse
import asyncio
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import RepeatedTimer, StarkboardDatabase, Requester
from starkboard.events.events import get_events, BlockEventsParser
from starkboard.transactions import transactions_in_block, get_transfer_transactions_in_block#, get_swap_info_in_block
from starkboard.user import count_wallet_deploy_in_block, get_active_wallets_in_block
from starkboard.contracts import count_contract_deployed_in_block, get_declared_class_in_block
from starkboard.constants import EVENT_KEYS_RETAINER
from starkboard.tokens import get_eth_total_supply, get_balance_of
from starkboard.fees import get_fees_in_block
from monitor import monitor_deployed_contracts
import signal
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--transfer_catching", help="Boolean to execute transfer count pipeline", required=False)
parser.add_argument("-b", "--block_data", help="Boolean to execute block data pipeline", required=False)
parser.add_argument("-from", "--fromBlock", help="From Block", required=False)
parser.add_argument("-to", "--toBlock", help="To Block", required=False)
parser.add_argument("-n", "--network", help="Network to target", required=False)

def fetch_checkpoint(db):
    res = db.get_checkpoint_block()
    return res['block_number']


######################################################################
#    Block & Tx Fetcher                                              #
######################################################################

last_checked_block = int(os.environ.get("STARTING_BLOCK_FETCHER", 0))

def block_tx_fetcher(block_id, node, db, loop):
    print("---")
    current_block = transactions_in_block(block_id, starknet_node=node)
    if 'code' in current_block:
        print("Still same block...")
        return None, None, None, None, None, None, block_id - 1
    events = get_events(block_id, starknet_node=node)
    wallet_deployed = count_wallet_deploy_in_block(events)
    contract_deployed = count_contract_deployed_in_block(current_block['transactions'])
    transfer_executed = get_transfer_transactions_in_block(events)
    fees = get_fees_in_block(current_block['transactions'], starknet_node=node)
    active_wallets = get_active_wallets_in_block(current_block['transactions'])
    print("Here")
    print(f'Fetched Block {current_block["block_number"]} at {datetime.fromtimestamp(current_block["timestamp"])}')
    print(f'> {len(current_block["transactions"])} Txs found in block.')
    print(f'> {wallet_deployed["deployed_wallets"]} User Wallet created in block.')
    print(f'> {contract_deployed["count_deployed_contracts"]} Contract deployed in block.')
    print(f'> {transfer_executed["count_transfer"]} Transfer executed in block.')
    print(f'> {fees["total_fees"]} Total fees in block.')
    print(f'> {fees["mean_fees"]} Average fees in block.')
    print(f'> {active_wallets["count_active_wallets"]} Active wallets found in block.')
    get_declared_class_in_block(current_block['transactions'], node, db)
    monitor_deployed_contracts(current_block['transactions'], current_block['timestamp'], node, db, loop)
    filtered_events = list(filter(lambda x: int(x['from_address'], 16) != int("0x12fadd18ec1a23a160cc46981400160fbf4a7a5eed156c4669e39807265bcd4", 16), events))
    block_events_parser = BlockEventsParser(filtered_events, current_block['timestamp'], fees['fee_per_tx'], node, db, loop)
    formatted_events = list(filter(lambda x: x['event_key'] in EVENT_KEYS_RETAINER, block_events_parser.events))
    db.insert_events_bulk(formatted_events)
#   get_transactions_info_in_block # get the different events counts and fees
#    get_swap_info_in_block(current_block["timestamp"], events, node, db, loop)
    return current_block, wallet_deployed, contract_deployed, transfer_executed, fees, active_wallets, current_block["block_number"]


def block_aggreg_fetcher(db, node):
    global last_checked_block
    print(f'Checking next block {last_checked_block + 1}')
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        current_block, wallet_deployed, contract_deployed, transfer_executed, fees, active_wallets, current_block_number = block_tx_fetcher(last_checked_block + 1, node, db, loop)
        loop.close()
        if not current_block:
            print("Connection timed out, retrying...")
            return True
    except Exception as e:
        print(e)
        print("Connection timed out, retrying...")
        return True
    block_data = {
        "block_number": current_block["block_number"],
        "timestamp": datetime.fromtimestamp(current_block["timestamp"]).strftime('%Y-%m-%d %H:%M:%S'),
        "full_day": datetime.fromtimestamp(current_block["timestamp"]).strftime('%Y-%m-%d'),
        "count_txs": len(current_block["transactions"]),
        "count_new_wallets": wallet_deployed["deployed_wallets"],
        "count_new_contracts": contract_deployed["count_deployed_contracts"],
        "count_transfers": transfer_executed["count_transfer"],
        "total_fees": fees["total_fees"],
        "mean_fees": fees["mean_fees"],
        "wallets_active": active_wallets['wallets_active']
    }
    insert_res = db.insert_block_data(block_data)
    if insert_res:
        print("Block Inserted !")
        last_checked_block = current_block_number
    else:
        print("Error Inserting Block. Retrying")
    return True

######################################################################
#    TVL, ERC20 & ETH data                                           #
######################################################################

async def ethereum_stats():
    """
    Getting Ethereum Statistics on Starknet
    """
    await get_eth_total_supply()


######################################################################
#            User Data                                               #
######################################################################

async def get_wallets_balance():
    with open("testnet_wallets.txt") as file:
        for address in file:
            bal = await get_balance_of(address, "ETH")
            print(f'Wallet {address} has {bal} ETH')


def handler(signum, frame):
    rt.stop()
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
    else:
        rt.start()
 
signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.network == "mainnet":
        delay = 30
        starknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
        starknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL_MAINNET"), headers={"Content-Type": "application/json"})
    else:
        starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        starknet_sequencer = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})
        delay = 5
    starkboard_db = StarkboardDatabase(args.network)
    if args.block_data:
        last_checked_block = fetch_checkpoint(starkboard_db)
        rt = RepeatedTimer(delay, block_aggreg_fetcher, starkboard_db, starknet_node)
