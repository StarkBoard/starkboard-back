import os
from starkboard.utils import StarkboardDatabase, Requester
from starkboard.transactions import transactions_in_block
from monitor import monitor_deployed_contracts
from starkboard.ecosystem.social import socials_metrics
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    #socials_metrics()
    starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
    db = StarkboardDatabase("testnet")
    for block in range(298700, 299304):#320000
        block_transactions = transactions_in_block(block, starknet_node=starknet_node)
        monitor_deployed_contracts(starknet_node, db, block_transactions)
