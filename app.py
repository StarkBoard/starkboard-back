import os
from flask import Flask
from dotenv import load_dotenv
from starkboard.utils import Requester
from datetime import datetime, time, timedelta

midnight = datetime.combine(datetime.today(), time.min)
yesterday_midnight = midnight - timedelta(days=1)

load_dotenv()

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

starknet_indexer = Requester(os.environ.get("STARKNET_INDEXER_URL"), headers={"Content-Type": "application/json"})
yesterday_block = starknet_indexer.get_block_from_timestamp(yesterday_midnight)
today_block = starknet_indexer.get_block_from_timestamp(midnight)


def get_yesterday_block():
    global yesterday_block;
    global today_block;
    midnight = datetime.combine(datetime.today(), time.min)
    yesterday_midnight = midnight - timedelta(days=1)
    diff = (datetime.combine(datetime.today(), time.min) - datetime.fromtimestamp(yesterday_block["timestamp"]))
    if diff.days == 1 and diff.seconds > 300:
        yesterday_block = starknet_indexer.get_block_from_timestamp(yesterday_midnight)
        today_block = starknet_indexer.get_block_from_timestamp(midnight)

    return yesterday_block, today_block

import starkboard.routes


if __name__ == '__main__':
    app.run()