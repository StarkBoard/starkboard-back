import os
import base64
import json
import gzip
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from starkboard.contracts import get_class_program, classify_hash_contract, get_hash_contract_info


def monitor_deployed_contracts(staknet_node, db, block_transactions):
    deploy_txs = [tx for tx in block_transactions["transactions"] if tx["type"] == "DEPLOY"]
    if deploy_txs:
        for tx in deploy_txs:
            for attempt in range(10):
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
                else:
                    break
