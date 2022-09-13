import os
import json
from starkboard.utils import Requester

if os.environ.get("IS_MAINNET") == "True":
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
else:
    staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})

def get_block_fees(block_id, starknet_node=None):
    """
    Retrieve the fees of a block
    """
    if block_id is None:
        r = starknet_node.post("", method="starknet_blockNumber")
        block_id = json.loads(r.text)["result"]
    params = {
        "block_number": block_id
    }
    r = starknet_node.post("", method="starknet_getBlockWithTxs", params=[params])
    data = json.loads(r.text)
    if 'error'in data:
        return data['error']
    block_txs = data["result"]["transactions"]
    transactions = [tx for tx in block_txs if tx["type"] != "DEPLOY"]
    total_fees = 0
    for transaction in transactions:
        try:
            actual_fee_request = starknet_node.post("", method="starknet_getTransactionReceipt", params=transaction)
            data_tx = json.loads(actual_fee_request.text)
            total_fees += int(data_tx["result"]["actual_fee"], 16) / 1e18
        except Exception as e:
            print(e)
            pass
    if len(transactions) > 0:
        mean_fees = total_fees / len(transactions)
    else:
        mean_fees = 0
    fees_params = {
        "total_fees": total_fees,
        "mean_fees": mean_fees
    }
    return fees_params
    