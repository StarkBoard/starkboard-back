import os
import pandas as pd
import json
from collections import Counter
from functools import reduce
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import StarkboardDatabase
from starkboard.ecosystem.social import socials_metrics

def get_block_data_by_date(db):
    daily_data = db.get_daily_data_from_blocks()
    for day_count, daily in enumerate(daily_data):
        daily['list_wallets_active'] = json.loads('[' + (daily.get('list_wallets_active') or '') + ']')
        list_wallets = list(map(lambda x: Counter(x), daily['list_wallets_active']))
        if len(list_wallets) > 0:
            list_wallets = reduce((lambda x, y: x + y), list_wallets)
        list_wallets = {k: v for k, v in sorted(dict(list_wallets).items(), key=lambda item: item[1], reverse=True)}
        daily['count_wallets_active'] = len(list_wallets)
        if list_wallets == {}:
            daily['top_wallets_active'] = []
        else:
            daily['top_wallets_active'] = list(list_wallets.keys())[:5]
        print(f'Inserting data on {daily["day"]}')
        db.insert_daily_data(daily)
        if day_count > 7: return None
    return None


def get_block_mints_data_by_date(db):
    daily_data_df = pd.DataFrame(db.get_daily_tvl_data_from_blocks())
    daily_data_deposit = pd.DataFrame(db.get_daily_average_deposit_data_from_blocks())
    daily_data_df = pd.merge(daily_data_df, daily_data_deposit, on=['day','token'])
    list_tokens = daily_data_df.token.unique().tolist()
    for token in list_tokens:
        sub_daily = daily_data_df[daily_data_df.token == token].to_dict('records')
        for day_count, daily in enumerate(sub_daily):
            print(f'Inserting TVL data on {daily["day"]} for {token}')
            db.insert_daily_tvl_data(daily)
            if day_count > 7: break


def get_block_transfers_data_by_date(db):
    daily_data_df = pd.DataFrame(db.get_daily_transfer_data_from_blocks())
    list_tokens = daily_data_df.token.unique().tolist()
    for token in list_tokens:
        sub_daily = daily_data_df[daily_data_df.token == token].to_dict('records')
        for day_count, daily in enumerate(sub_daily):
            print(f'Inserting Transfers data on {daily["day"]} for {token}')
            db.insert_daily_transfers_data(daily)
            if day_count > 7: break


def get_events_data_by_date(db):
    daily_swaps = db.get_daily_swap_events()
    for day_count, daily in enumerate(daily_swaps):
        data = {
            "volume_token0": daily['volume_token0'],
            "volume_token1": daily['volume_token1']
        }
        daily['data'] = json.dumps(data)
        print(f'Inserting data on {daily["day"]}')
        db.insert_daily_events(daily)


def test_func(db):
    daily_data = db.get_daily_data_from_blocks()
    print(daily_data[20].get('list_wallets_active'))


if __name__ == '__main__':
    print("Indexing Data for Testnet...")
    starkboard_db = StarkboardDatabase("testnet")
    get_block_data_by_date(starkboard_db)
    get_block_mints_data_by_date(starkboard_db)
    get_block_transfers_data_by_date(starkboard_db)
    get_events_data_by_date(starkboard_db)
    print("Testned indexed !")
    print("Indexing Data for Mainnet...")
    starkboard_db = StarkboardDatabase("mainnet")
    get_block_data_by_date(starkboard_db)
    get_block_mints_data_by_date(starkboard_db)
    get_block_transfers_data_by_date(starkboard_db)
    get_events_data_by_date(starkboard_db)
    print("Mainnet indexed !")
    print("OffChain Indexing....")
    socials_metrics()
    print("OffChain Indexing done !")
