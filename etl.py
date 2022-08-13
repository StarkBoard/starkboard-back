import os
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


def test_func(db):
    print(db.get_historical_daily_data())


if __name__ == '__main__':
    print("Indexing Data for Testnet...")
    starkboard_db = StarkboardDatabase("testnet")
    get_block_data_by_date(starkboard_db)
    print("Testned indexed !")
    print("Indexing Data for Mainnet...")
    starkboard_db = StarkboardDatabase("mainnet")
    get_block_data_by_date(starkboard_db)
    print("Mainnet indexed !")
