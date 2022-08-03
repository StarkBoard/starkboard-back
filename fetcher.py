import os
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import RepeatedTimer, StarkboardDatabase
from starkboard.transactions import transactions_in_block, get_transfer_transactions_in_block
from starkboard.user import count_wallet_deployed, get_wallet_address_deployed
from starkboard.contracts import count_contract_deployed_int_block
from starkboard.tokens import get_eth_total_supply, get_balance_of
import signal
import asyncio
from datetime import datetime



######################################################################
#    Block & Tx Fetcher                                              #
######################################################################

last_checked_block = int(os.environ.get("STARTING_BLOCK_FETCHER", transactions_in_block("latest")["block_number"]))
print(f'Init with block {last_checked_block}')

def block_tx_fetcher(block_id):
    current_block = transactions_in_block(block_id)
    if 'code' in current_block:
        print("Still same block...")
        return None, None, None, None, block_id - 1

    wallet_deployed = count_wallet_deployed(wallet_type="All", fromBlock=block_id, toBlock=block_id)
    contract_deployed = count_contract_deployed_int_block(block_id)
    transfer_executed = get_transfer_transactions_in_block(block_id)

    print("---")
    print(f'Fetched Block {current_block["block_number"]} at {datetime.fromtimestamp(current_block["accepted_time"])}')
    print(f'> {len(current_block["transactions"])} Txs found in block.')
    print(f'> {wallet_deployed["deployed_wallets"]} User Wallet created in block.')
    print(f'> {contract_deployed["count_deployed_contracts"]} Contract deployed in block.')
    print(f'> {transfer_executed["count_transfer"]} Transfer executed in block.')

    return current_block, wallet_deployed, contract_deployed, transfer_executed, current_block["block_number"]


def block_aggreg_fetcher(db):
    global last_checked_block
    print(f'Checking next block {last_checked_block + 1}')
    current_block, wallet_deployed, contract_deployed, transfer_executed, current_block_number = block_tx_fetcher(last_checked_block + 1)
    block_data = {
        "block_number": current_block["block_number"],
        "timestamp": datetime.fromtimestamp(current_block["accepted_time"]).strftime('%Y-%m-%d %H:%M:%S'),
        "full_day": datetime.fromtimestamp(current_block["accepted_time"]).strftime('%Y-%m-%d'),
        "count_txs": len(current_block["transactions"]),
        "count_new_wallets": wallet_deployed["deployed_wallets"],
        "count_new_contracts": contract_deployed["count_deployed_contracts"],
        "count_transfers": transfer_executed["count_transfer"]
    }
    print(block_data)
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


def user_wallets_storage():
    list_wallets = get_wallet_address_deployed(wallet_type="All", fromBlock=270000, toBlock=285030)
    with open('testnet_wallets.txt', 'w') as f:
        for wallet in list_wallets:
            f.write(f"{wallet}\n")
    return list_wallets


async def get_wallets_balance():
    with open("testnet_wallets.txt") as file:
        for address in file:
            print(address)
            await get_balance_of(address, "ETH")


def handler(signum, frame):
    rt.stop()
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
    else:
        rt.start()
 
signal.signal(signal.SIGINT, handler)


if __name__ == '__main__':
    starkboard_db = StarkboardDatabase()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(get_wallets_balance())
    rt = RepeatedTimer(5, block_aggreg_fetcher, starkboard_db)
