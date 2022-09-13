import os
import base64
import json
import gzip
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import Requester, StarkboardDatabase, get_twitter_api_auth, get_application_follower
from starkboard.transactions import transactions_in_block, state_update
from starkboard.contracts import get_class_program, classify_hash_contract, get_hash_contract_info

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


def monitor_deployed_contracts(staknet_node, db, block_transactions):
    deploy_txs = [tx for tx in block_transactions["transactions"] if tx["type"] == "DEPLOY"]
    if deploy_txs:
        for tx in deploy_txs:
            try:
                class_hash = tx.get('class_hash')
                # Check DB
                db_class_hash_type = db.get_contract_hash(class_hash)
                if db_class_hash_type:
                    deployed_contract_type, event_keys = get_hash_contract_info(db_class_hash_type.get('type'))
                else:
                    prog = get_class_program(class_hash, staknet_node)
                    base64_bytes = prog.encode('utf-8')
                    message_bytes = base64.b64decode(base64_bytes)
                    json_code = json.loads(gzip.decompress(message_bytes).decode()).get('identifiers')
                    main_functions = list(filter(lambda x: '__main__' in x, list(json_code.keys())))
                    final_functions = set(list(map(lambda x: x.split('.')[1], main_functions)))
                    deployed_contract_type, event_keys = classify_hash_contract(final_functions)
                if deployed_contract_type:
                    if not db_class_hash_type:
                        newly_hash_found = {
                            "class_hash": class_hash,
                            "type": deployed_contract_type
                        }
                        db.insert_contract_hash(newly_hash_found)
                    newly_contract_found = {
                        "contract_address": tx.get("contract_address"),
                        "application": "Unknown",
                        "event_keys": event_keys,
                        "class_hash": class_hash,
                        "type": deployed_contract_type,
                        "deployed_at": datetime.fromtimestamp(block_transactions.get('timestamp')).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    db.insert_contract_type(newly_contract_found)
                    print(f'✨ New Contract Deployed Identified ! {tx.get("contract_address")} has been identified as an {deployed_contract_type}')
            except Exception as e:
                print(e)
                continue

if __name__ == '__main__':
    socials_metrics()
