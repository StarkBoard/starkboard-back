from app import app
from starkboard.transactions import transactions_in_block
from starkboard.fees import estimate_fees


@app.route('/', methods=['GET'])
def landing():
    return 'ODA API'

#######################
# Transactions Routes #
#######################

@app.route('/getTxInBlock', methods=['GET'])
def get_transactions_in_block():
    """
    Retrieve the list of transactions hash from a given block number
    """
    return transactions_in_block()


#######################
#    Fees Routes      #
#######################

@app.route('/estimateFee', methods=['GET'])
def get_estimate_fees():
    """
    Fees Estimation on the network
    """
    return estimate_fees()
