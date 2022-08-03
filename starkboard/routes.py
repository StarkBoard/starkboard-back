from imaplib import _Authenticator
from app import app
from flask import request
from starkboard.transactions import transactions_in_block
from starkboard.contracts import count_contract_deployed_current_block
from starkboard.utils import StarkboardDatabase

@app.route('/', methods=['GET'])
def landing():
    return 'ODA API'


#######################
#    General Route    #
#######################
#######################
@app.route('/store_starkboard_og', methods=['POST'])
def store_starkboard_og():
    """
    Stores a wallet OG with its signature
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase()
    insert_res = starkboard_db.inserts_starkboard_og(data)
    starkboard_db.close_connection()
    if insert_res:
        return {
            'result': f'Successfully inserted OG {data["wallet_address"]}'
        }, 200
    else:
        return {
            'result': f'OG {data["wallet_address"]} already registered'
        }, 400


@app.route('/get_starkboard_og', methods=['POST'])
def get_starkboard_og():
    """
    Stores a wallet OG with its signature
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase()
    res = starkboard_db.get_starkboard_og(data)
    starkboard_db.close_connection()
    return res, 200


#######################
# Transactions Routes #
#######################
@app.route('/getTxInBlock', methods=['GET'])
def get_transactions_in_block():
    """
    Retrieve the list of transactions hash from a given block number
    """
    return transactions_in_block()


@app.route('/getDailyCountTransfer', methods=['GET'])
def get_daily_count_transfer():
    """
    Retrieve the daily number of tranfer transactions type
    TBD
    """
    return {}


#######################
#    User Routes      #
#######################
@app.route('/getDailyCountWalletDeployed', methods=['GET'])
def get_count_wallet_deployed():
    """
    Retrieve the daily number of Wallets deployed (ArgentX or Braavos or All)
    TBD
    """
    return {}


#######################
#  Contracts Routes   #
#######################
@app.route('/getCurrentBlockCountContractsDeployed', methods=['GET'])
def get_count_contrats_deployed_current_block():
    """
    Retrieve the number of Contract deployed on StarkNet on the latest block
    """
    return count_contract_deployed_current_block()

@app.route('/getMostUsedFunctionFromContract', methods=['GET'])
def get_most_used_functions_from_contract():
    """
    Retrieve the most used functions of a Smart Contract with Count
    TBD
    """
    return {}


#######################
#    Fees Routes      #
#######################

@app.route('/estimateFee', methods=['GET'])
def get_estimate_fees():
    """
    Fees Estimation on the network
    TBD
    """
    return {}
