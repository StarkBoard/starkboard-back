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
        for tx in block_transactions.get('transactions'):
            if tx.get('type') == "DEPLOY" and tx.get('class_hash') not in ["0x726edb35cc732c1b3661fd837592033bd85ae8dde31533c35711fb0422d8993", "0x23e92706bf099b3949766ae08206c25c4228fbcc9f0bffc6ed042442bfaf55a", "0x4e733f6eb56ba1032e102312b52aaf7680f2a9f539970cd2791a57a0ad3f4c7", "0x25ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918", "0x3131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e", "0x2864c45bd4ba3e66d8f7855adcadf07205c88f43806ffca664f1f624765207e", "0x1ca349f9721a2bf05012bb475b404313c497ca7d6d5f80c03e98ff31e9867f5"]:
                print(tx.get('class_hash'))

        #monitor_deployed_contracts(starknet_node, db, block_transactions)
