import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.transactions import transactions_in_block
from starkboard.contracts import get_declared_class_in_block
from monitor import monitor_deployed_contracts
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    for block in range(320000, 330000):
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        #monitor_deployed_contracts(block_transactions['transactions'], block_transactions['timestamp'], starknet_node, db)
        declared_tx = [tx for tx in block_transactions['transactions'] if tx["type"] == "DECLARE"]
        if declared_tx:
            print(f'Declared a contract at block {block}')
            get_declared_class_in_block(declared_tx, starknet_node, db)
