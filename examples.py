import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.ecosystem.fetch_application import update_core_ecosystem
from starkboard.transactions import transactions_in_block, state_update
from monitor import monitor_deployed_contracts

import base64
import gzip
import json
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    for block in range(250000, 300000):
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        monitor_deployed_contracts(starknet_node, db, block_transactions)
