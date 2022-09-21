import json
import numpy as np
from collections import defaultdict, Counter
from functools import reduce

from starkboard.utils import get_leaves
from starkboard.constants import WALLET_KEYS
from starkboard.tokens import get_balance_of, get_nonce_of
from starkboard.events.events import filter_events

mainnet_ranking = list()
testnet_ranking = list()

def count_wallet_deploy_in_block(events):
    deployed_wallet_events = filter_events(events, WALLET_KEYS["All"])
    braavos_count = list(filter(lambda event: event['keys'][0] in WALLET_KEYS["Braavos"], deployed_wallet_events))
    argentx_count = list(filter(lambda event: event['keys'][0] in WALLET_KEYS["ArgentX"], deployed_wallet_events))
    count_wallet = len(deployed_wallet_events)
    return {
        "deployed_wallets": count_wallet,
        "braavos_deployed_wallets": braavos_count,
        "argentx_deployed_wallets": argentx_count
    }

def get_active_wallets_in_block(block_txs=[]):
    """
    Retrieve the number of active wallets in block
    """
    senders_tx = [tx['contract_address'] for tx in block_txs if tx["type"] == "INVOKE" and len(tx['signature']) > 0]
    list_wallets = defaultdict(int)
    for s in senders_tx: list_wallets[s] += 1 
    sorted_list_wallets = {k: v for k, v in sorted(list_wallets.items(), key=lambda item: item[1], reverse=True)}
    return {
        'count_active_wallets': len(sorted_list_wallets),
        'wallets_active': sorted_list_wallets
    }


def fetch_wallets_ranking(db_main, db_test):
    """
    Retrieve the number of active wallets in block
    """
    global testnet_ranking
    global mainnet_ranking
    print("Cron RUNNING : mainnet...")
    raw_wallets_info = db_main.get_wallets_info_blocks()
    list_wallets = []
    for info in raw_wallets_info:
        list_wallets.append(json.loads('['+info['list_wallets_active']+']')[0])
    list_wallets = list(map(lambda x: Counter(x), list_wallets))
    list_wallets = reduce((lambda x, y: x + y), list_wallets)
    wallets = {k: v for k, v in sorted(list_wallets.items(), key=lambda item: item[1], reverse=True)}
    list_wallets = list(wallets)[:15]
    wallet_ranking = []
    for address in list_wallets:
        eth_balance = get_balance_of(address, network="mainnet")
        nonce = get_nonce_of(address, network="mainnet")
        current_res = {
            "wallet_address": address,
            "monthly_txs": wallets[address],
            "eth": eth_balance,
            "count_txs": nonce
        }
        wallet_ranking.append(current_res)
    mainnet_ranking = wallet_ranking
    print("Cron FINISHED : mainnet!")
    print("Cron RUNNING : testnet...")
    raw_wallets_info = db_test.get_wallets_info_blocks()
    list_wallets = []
    for info in raw_wallets_info:
        list_wallets.append(json.loads('['+info['list_wallets_active']+']')[0])
    list_wallets = list(map(lambda x: Counter(x), list_wallets))
    list_wallets = reduce((lambda x, y: x + y), list_wallets)
    wallets = {k: v for k, v in sorted(list_wallets.items(), key=lambda item: item[1], reverse=True)}
    list_wallets = list(wallets)[:15]
    wallet_ranking = []
    for address in list_wallets:
        eth_balance = get_balance_of(address, network="testnet")
        nonce = get_nonce_of(address, network="testnet")
        current_res = {
            "wallet_address": address,
            "monthly_txs": wallets[address],
            "eth": eth_balance,
            "count_txs": nonce
        }
        wallet_ranking.append(current_res)
    testnet_ranking = wallet_ranking
    print("Cron FINISHED : testnet!")


def use_wallets_ranking(network="testnet"):
    if network == "testnet":
        return testnet_ranking
    else:
        return mainnet_ranking

#######################
#      Whitelists     #
#######################

def fetch_whitelist(db, wl_type):
    if wl_type == 0:
        sql_query = f"""SELECT * FROM starkboard_og ORDER BY user_rank ASC LIMIT 2000"""
    elif wl_type == 1:
        sql_query = f"""SELECT * FROM starkboard_og ORDER BY user_rank ASC LIMIT 3000 OFFSET 2000"""
    else:
        sql_query = f"""SELECT * FROM starkboard_og WHERE user_rank > 7885 ORDER BY RAND() ASC LIMIT 1000"""
    cursor = db.execute_query(sql_query)
    res = cursor.fetchall()
    cursor.close()
    db.close_connection()
    return res

def leaves_results(whitelisted):
    wl = list(map(lambda wl: int(wl.get('wallet_address'), 16), whitelisted))
    return wl, list(np.ones(len(whitelisted), int))

def whitelist(db, wl_type=0):
    whitelisted = fetch_whitelist(db, wl_type)
    wallets, amount = leaves_results(whitelisted)
    merkle_info = get_leaves(
        wallets,
        amount
    )
    leaves = list(map(lambda x: x[0], merkle_info))
    db.close_connection()
    return wallets, leaves
