from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from starkboard.contracts import get_class_info, get_proxy_contract, get_contract_info


def monitor_deployed_contracts(block_transactions, timestamp, starknet_node, db, loop):
    deploy_txs = [tx for tx in block_transactions if tx["type"] == "DEPLOY"]
    if deploy_txs:
        for tx in deploy_txs:
            for attempt in range(10):
                try:
                    class_hash = tx.get('class_hash')
                    if class_hash in ["0x10455c752b86932ce552f2b0fe81a880746649b9aee7e0d842bf3f52378f9f8", 
                        "0x1ca349f9721a2bf05012bb475b404313c497ca7d6d5f80c03e98ff31e9867f5",
                        "0x590267e2a8bdb5a5c5c6b8f51751fc661866d96e6dec956f8562f54ecdffabc", 
                        "0xa69700a89b1fa3648adff91c438b79c75f7dcb0f4798938a144cce221639d6",
                        "0x4572af1cd59b8b91055ebb78df8f1d11c59f5270018b291366ba4585d4cdff0"]:
                        break
                    contract_info = loop.run_until_complete(get_contract_info(tx.get('contract_address'), starknet_node, db, class_hash, timestamp))
                    print(f'✨ New Contract Deployed Identified ! {tx.get("contract_address")} has been identified as an {contract_info.get("type")}')
                except Exception as e:
                    print(e)
                    continue
                else:
                    break
