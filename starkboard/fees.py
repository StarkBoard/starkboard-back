import json

def get_fees_in_block(block_txs, starknet_node=None):
    """
    Retrieve the fees of a block
    """
    transactions = [tx for tx in block_txs if tx["type"] not in ["DEPLOY"]]
    total_fees = 0
    fee_per_tx = {}
    for transaction in transactions:
        try:
            actual_fee_request = starknet_node.post("", method="starknet_getTransactionReceipt", params=transaction)
            data_tx = json.loads(actual_fee_request.text)
            actual_fee = int(data_tx["result"]["actual_fee"], 16) / 1e18
            total_fees += actual_fee
            fee_per_tx[transaction['transaction_hash']] = actual_fee
        except Exception as e:
            print(e)
            pass
    if len(transactions) > 0:
        mean_fees = total_fees / len(transactions)
    else:
        mean_fees = 0
    fees_params = {
        "total_fees": total_fees,
        "mean_fees": mean_fees,
        "fee_per_tx": fee_per_tx
    }
    return fees_params
    

def get_fees_in_tx(tx_hash, starknet_node=None):
    """
    Retrieve the fees of a block
    """
    try:
        actual_fee_request = starknet_node.post("", method="starknet_getTransactionReceipt", params=[tx_hash])
        data_tx = json.loads(actual_fee_request.text)
        return int(data_tx["result"]["actual_fee"], 16)
    except Exception as e:
        print(e)
        pass
