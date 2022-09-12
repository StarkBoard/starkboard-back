import os
import base64
import json
import gzip
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import Requester, StarkboardDatabase, get_twitter_api_auth, get_application_follower
from starkboard.transactions import transactions_in_block, state_update
from starkboard.contracts import class_hashes, get_class_program, classify_hash_contract

def socials_metrics():
    starkboard_db = StarkboardDatabase()
    list_ecosystem = starkboard_db.get_ecosystem_twitter_handlers()
    twitter_api = get_twitter_api_auth()
    for app in list_ecosystem:
        if app.get("twitter_handler"):
            public_metrics = get_application_follower(app.get("twitter_handler"), twitter_api)
            if not public_metrics:
                continue
            print(f'Retrieved Social metrics for {app.get("twitter_handler")}')
            print(public_metrics)
            updated_data = {
                "application": app.get("application"),
                "followers_count": public_metrics.get("followers_count"),
                "tweet_count": public_metrics.get("tweet_count")
            }
            starkboard_db.update_ecosystem_twitter_social(updated_data)


def monitor_deployed_contracts(staknet_node, block_transactions):
    deploy_txs = [tx for tx in block_transactions["transactions"] if tx["type"] == "DEPLOY"]
    if deploy_txs:
        list_class_hash = set([tx.get('class_hash') for tx in deploy_txs])
        for class_hash in list_class_hash:
            prog = get_class_program(class_hash, staknet_node)
            base64_bytes = prog.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            json_code = json.loads(gzip.decompress(message_bytes).decode()).get('identifiers')
            main_functions = list(filter(lambda x: '__main__' in x, list(json_code.keys())))
            final_functions = set(list(map(lambda x: x.split('.')[1], main_functions)))
            classify_hash_contract(class_hash, final_functions)


if __name__ == '__main__':
    socials_metrics()
