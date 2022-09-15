import os
import argparse
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import RepeatedTimer, StarkboardDatabase, Requester, chunks
from starkboard.transactions import get_transfer_transactions
from starkboard.user import get_active_wallets_in_block
from starkboard.tokens import get_eth_total_supply, get_balance_of
import signal
import time


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--transfer_catching", help="Boolean to execute transfer count pipeline", required=False)
parser.add_argument("-f", "--fees_catching", help="Boolean to execute fees_catching pipeline", required=False)
parser.add_argument("-u", "--users_catching", help="Boolean to execute Users_catching pipeline", required=False)
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

## Catcher

def update_transfer_count(db, fromBlock, toBlock, node):
    range_block = chunks(range(fromBlock, toBlock), 200)
    for rg in range_block:
        for attempt in range(50):
            try:
                print(f'Fetching from block {rg[0]} to {rg[-1]}...')
                transfer_executed = get_transfer_transactions(rg[0], rg[-1], node)
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

def catch_users(db, fromBlock, toBlock, node):
    for block_number in range(fromBlock, toBlock):
        for attempt in range(50):
            try:
                data = get_active_wallets_in_block(block_number, node)
                db.update_block_users(block_number, data)
            except Exception as e:
                print(e)
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
    else:
        starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        delay = 1
    starkboard_db = StarkboardDatabase(args.network)
    if args.transfer_catching:
        update_transfer_count(starkboard_db, int(args.fromBlock), int(args.toBlock), starknet_node)
    if args.users_catching:
        catch_users(starkboard_db, int(args.fromBlock), int(args.toBlock), starknet_node)
