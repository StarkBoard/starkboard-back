import os
import json
from collections import defaultdict
from starkboard.utils import Requester, get_leaves
import numpy as np

wallet_key = {
    "ArgentX": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784"],
    "Braavos": ["0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"],
    "All": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784", "0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"]
}

def count_wallet_deployed(wallet_type="All", fromBlock=0, toBlock=0, starknet_node=None):
    """
    Retrieve the number of ArgentX or Braavos wallet Deployed
    Braavos key : 0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049
    ArgentX key : 0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784
    """
    params = {
        "filter": {
            "fromBlock": {
                "block_number": fromBlock
            }, 
            "toBlock": {
                "block_number": toBlock
            }, 
            "page_size": 500,
            "page_number": 0, 
            "keys": wallet_key[wallet_type]
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    count_wallet = len(data["events"])
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        count_wallet += len(data["events"])

    return {
        "deployed_wallets": count_wallet
    }


def get_wallet_address_deployed(wallet_type="All", fromBlock=0, toBlock=0, starknet_node=None):
    """
    Retrieve the number of ArgentX or Braavos wallet Deployed
    Braavos key : 0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049
    ArgentX key : 0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784
    """
    params = {
        "filter": {
            "fromBlock": {
                "block_number": fromBlock
            }, 
            "toBlock": {
                "block_number": toBlock
            }, 
            "page_size": 1024,
            "page_number": 0, 
            "keys": wallet_key[wallet_type]
        }
    }

    r = starknet_node.post("", method="starknet_getEvents", params=params)
    data = json.loads(r.text)["result"]
    list_wallet_address = [event["from_address"] for event in data["events"]]
    print(f'{len(list_wallet_address)} Wallets found currently...')
    while not data["is_last_page"]:
        params["filter"]["page_number"] += 1
        r = starknet_node.post("", method="starknet_getEvents", params=params)
        data = json.loads(r.text)["result"]
        list_wallet_address += [event["from_address"] for event in data["events"]]
        print(f'{len(list_wallet_address)} Wallets found currently...')

    return list_wallet_address



def get_active_wallets_in_block(block_number=0, starknet_node=None):
    """
    Retrieve the number of active wallets in block
    """
    params = {
        "block_number": block_number
    }
    r = starknet_node.post("", method="starknet_getBlockWithTxs", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    block_txs = data["result"]["transactions"]
    senders_tx = [tx['contract_address'] for tx in block_txs if tx["type"] == "INVOKE" and tx['signature']]
    list_wallets = defaultdict(int)
    for s in senders_tx: list_wallets[s] += 1 
    sorted_list_wallets = {k: v for k, v in sorted(list_wallets.items(), key=lambda item: item[1], reverse=True)}
    return {
        'count_active_wallets': len(sorted_list_wallets),
        'wallets_active': sorted_list_wallets
    }


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
    return wallets, leaves
