import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import StarkboardDatabase


def get_block_data_by_date(db):
    daily_data = db.get_daily_data_from_blocks()
    for day_count, daily in enumerate(daily_data):
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
        for daily in sub_daily:
            print(f'Inserting TVL data on {daily["day"]} for {token}')
            db.insert_daily_tvl_data(daily)


def get_block_transfers_data_by_date(db):
    daily_data_df = pd.DataFrame(db.get_daily_transfer_data_from_blocks())
    list_tokens = daily_data_df.token.unique().tolist()
    for token in list_tokens:
        sub_daily = daily_data_df[daily_data_df.token == token].to_dict('records')
        for daily in sub_daily:
            print(f'Inserting Transfers data on {daily["day"]} for {token}')
            db.insert_daily_transfers_data(daily)



def test_func(db):
    daily_data_df = pd.DataFrame(db.get_daily_tvl_data_from_blocks())


if __name__ == '__main__':
    print("Indexing Data for Testnet...")
    starkboard_db = StarkboardDatabase("testnet")
    get_block_data_by_date(starkboard_db)
    get_block_mints_data_by_date(starkboard_db)
    get_block_transfers_data_by_date(starkboard_db)
    print("Testned indexed !")
    print("Indexing Data for Mainnet...")
    starkboard_db = StarkboardDatabase("mainnet")
    get_block_data_by_date(starkboard_db)
    get_block_mints_data_by_date(starkboard_db)
    get_block_transfers_data_by_date(starkboard_db)
    print("Mainnet indexed !")
