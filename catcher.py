import os
import argparse
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import RepeatedTimer, StarkboardDatabase, Requester, chunks
from starkboard.transactions import transactions_in_block, get_transfer_transactions_in_block, get_transfer_transactions, get_transfer_transactions_v2
from starkboard.user import count_wallet_deployed, get_wallet_address_deployed
from starkboard.contracts import count_contract_deployed_in_block
from starkboard.tokens import get_eth_total_supply, get_balance_of
import signal
import asyncio
from datetime import datetime
import time


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

def block_tx_fetcher(block_id, node):
    current_block = transactions_in_block(block_id, starknet_node=node)
    if 'code' in current_block:
        print("Still same block...")
        return None, None, None, None, block_id - 1
    wallet_deployed = count_wallet_deployed(wallet_type="All", fromBlock=block_id, toBlock=block_id, starknet_node=node)
    contract_deployed = count_contract_deployed_in_block(current_block)
    transfer_executed = get_transfer_transactions_in_block(block_id, starknet_node=node)
    print("---")
    print(f'Fetched Block {current_block["block_number"]} at {datetime.fromtimestamp(current_block["timestamp"])}')
    print(f'> {len(current_block["transactions"])} Txs found in block.')
    print(f'> {wallet_deployed["deployed_wallets"]} User Wallet created in block.')
    print(f'> {contract_deployed["count_deployed_contracts"]} Contract deployed in block.')
    print(f'> {transfer_executed["count_transfer"]} Transfer executed in block.')

    return current_block, wallet_deployed, contract_deployed, transfer_executed, current_block["block_number"]


def block_aggreg_fetcher(db, node):
    global last_checked_block
    print(f'Checking next block {last_checked_block + 1}')
    try:
        current_block, wallet_deployed, contract_deployed, transfer_executed, current_block_number = block_tx_fetcher(last_checked_block + 1, node)
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
        "count_transfers": transfer_executed["count_transfer"]
    }
    insert_res = db.insert_block_data(block_data)
    if insert_res:
        print("Block Inserted !")
        last_checked_block = current_block_number
    else:
        print("Error Inserting Block. Retrying")
    return True



## Catcher

def block_tx_fetcher_fast(block_id, node):
    current_block = transactions_in_block(block_id, starknet_node=node)
    if 'code' in current_block:
        print("Still same block...")
        return None, None, None, None, block_id - 1
    wallet_deployed = count_wallet_deployed(wallet_type="All", fromBlock=block_id, toBlock=block_id, starknet_node=node)
    contract_deployed = count_contract_deployed_in_block(current_block)
    print("---")
    print(f'Fetched Block {current_block["block_number"]} at {datetime.fromtimestamp(current_block["timestamp"])}')
    print(f'> {len(current_block["transactions"])} Txs found in block.')
    print(f'> {wallet_deployed["deployed_wallets"]} User Wallet created in block.')
    print(f'> {contract_deployed["count_deployed_contracts"]} Contract deployed in block.')

    return current_block, wallet_deployed, contract_deployed, current_block["block_number"]



def block_aggreg_fetcher_fast(db, node):
    global last_checked_block
    print(f'Checking next block {last_checked_block + 1}')
    try:
        current_block, wallet_deployed, contract_deployed, current_block_number = block_tx_fetcher_fast(last_checked_block + 1, node)
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
        "count_transfers": 0
    }
    insert_res = db.insert_block_data(block_data)
    if insert_res:
        print("Block Inserted !")
        last_checked_block = current_block_number
    else:
        print("Error Inserting Block. Retrying")
    return True


def update_transfer_count(db, fromBlock, toBlock, node):
    range_block = chunks(range(fromBlock, toBlock), 200)
    for rg in range_block:
        for attempt in range(50):
            try:
                print(f'Fetching from block {rg[0]} to {rg[-1]}...')
                transfer_executed = get_transfer_transactions_v2(rg[0], rg[-1], node)
                print(transfer_executed)
                for block_number, count_transfer in transfer_executed.items():
                    db.update_block_data(block_number, count_transfer)
                time.sleep(1)
            except Exception as e:
                print("E:")
                print(e)
                print("Fetch Error...")
                continue
            else:
                break
            

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


def user_wallets_storage(node):
    list_wallets = get_wallet_address_deployed(wallet_type="All", fromBlock=270000, toBlock=285030, starknet_node=node)
    with open('testnet_wallets.txt', 'w') as f:
        for wallet in list_wallets:
            f.write(f"{wallet}\n")
    return list_wallets


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
        staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
    else:
        staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        delay = 1
    starkboard_db = StarkboardDatabase(args.network)
    if args.transfer_catching:
        update_transfer_count(starkboard_db, int(args.fromBlock), int(args.toBlock), staknet_node)
    if args.block_data:
        last_checked_block = fetch_checkpoint(starkboard_db)
        rt = RepeatedTimer(delay, block_aggreg_fetcher_fast, starkboard_db, staknet_node)
