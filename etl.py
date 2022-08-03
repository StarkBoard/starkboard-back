import os
from dotenv import load_dotenv
load_dotenv()

from starkboard.utils import StarkboardDatabase


def get_block_data_by_date(db):
    daily_data = db.get_daily_data_from_blocks()
    for daily in daily_data:
        db.insert_daily_data(daily)
    

    
    return None


if __name__ == '__main__':
    starkboard_db = StarkboardDatabase()
    get_block_data_by_date(starkboard_db)