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
                    if class_hash in ["0x10455c752b86932ce552f2b0fe81a880746649b9aee7e0d842bf3f52378f9f8", 
                        "0x25ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918", 
                        "0x3131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e", 
                        "0x1ca349f9721a2bf05012bb475b404313c497ca7d6d5f80c03e98ff31e9867f5",
                        "0x590267e2a8bdb5a5c5c6b8f51751fc661866d96e6dec956f8562f54ecdffabc", 
                        "0x71c3c99f5cf76fc19945d4b8b7d34c7c5528f22730d56192b50c6bbfd338a64",
                        "0x4d1f4cf4ef520c768a326d34f919227e1f075effda532f57cbaec6a1228db88",
                        "0xa69700a89b1fa3648adff91c438b79c75f7dcb0f4798938a144cce221639d6",
                        "0x4572af1cd59b8b91055ebb78df8f1d11c59f5270018b291366ba4585d4cdff0",
                        "0x5624a24901a556ec1f24594b6014948b72e5f6cc9c1d84594d5a0fb1b614917"]:
                        break
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
