from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from starkboard.contracts import get_declared_class


def monitor_deployed_contracts(block_transactions, timestamp, starknet_node, db):
    deploy_txs = [tx for tx in block_transactions if tx["type"] == "DEPLOY"]
    if deploy_txs:
        for tx in deploy_txs:
            for attempt in range(10):
                try:
                    class_hash = tx.get('class_hash')
                    contract_class = db.get_contract_hash(class_hash)
                    if not contract_class:
                        contract_class = get_declared_class(class_hash, starknet_node, db)
                    if contract_class:
                        newly_contract_found = {
                            "contract_address": tx.get("contract_address"),
                            "application": "Unknown",
                            "event_keys": contract_class.get("event_keys", "[]"),
                            "abi": contract_class.get("abi", "[]"),
                            "class_hash": class_hash,
                            "type": contract_class.get('type'),
                            "deployed_at": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        db.insert_contract_type(newly_contract_found)
                        print(f'✨ New Contract Deployed Identified ! {tx.get("contract_address")} has been identified as an {contract_class.get("type")}')
                except Exception as e:
                    print(e)
                    continue
                else:
                    break
