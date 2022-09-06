from datetime import datetime
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from starkboard.routes import app_routes
from cache import cache
import asyncio
from flask_apscheduler import APScheduler
from starkboard.utils import StarkboardDatabase
from starkboard.user import fetch_wallets_ranking

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
CORS(app)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

app.config.from_mapping(config)
cache.init_app(app)

app.register_blueprint(app_routes)


if __name__ == '__main__':
    db_mainnet = StarkboardDatabase("mainnet")
    db_testnet = StarkboardDatabase("testnet")
    class Config:
        JOBS = [
            {
                "id": "job1",
                "func": "starkboard.user:fetch_wallets_ranking",
                "args": (db_mainnet, db_testnet),
                "trigger": "interval",
                "seconds": 7200, #43200
                "next_run_time": datetime.now()
            }
        ]
        SCHEDULER_API_ENABLED = True
    app.config.from_object(Config())    
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host="0.0.0.0", port=8080)
