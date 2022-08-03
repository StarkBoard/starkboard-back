from imaplib import _Authenticator
from app import app
from flask import request
from starkboard.transactions import transactions_in_block, get_transfer_transactions_in_block
from starkboard.fees import estimate_fees
from starkboard.user import count_wallet_deployed
from starkboard.contracts import count_contract_deployed_current_block, most_used_functions_from_contract

@app.route('/', methods=['GET'])
def landing():
    return 'ODA API'


#######################
#    General Route    #
#######################
#######################
@app.route('/store_starkboard_og', methods=['POST'])
def get_transactions_in_block():
    """
    Stores a wallet OG with its signature
    """


    return transactions_in_block()


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
    """
    return get_transfer_transactions_in_block()


#######################
#    User Routes      #
#######################
@app.route('/getDailyCountWalletDeployed', methods=['GET'])
def get_count_wallet_deployed():
    """
    Retrieve the daily number of Wallets deployed (ArgentX or Braavos or All)
    """
    wallet_type = request.args.get('walletType', 'All')
    return count_wallet_deployed(wallet_type)


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
    """
    contract_address = request.args.get('contractAddress')
    return most_used_functions_from_contract(contract_address)


#######################
#    Fees Routes      #
#######################

@app.route('/estimateFee', methods=['GET'])
def get_estimate_fees():
    """
    Fees Estimation on the network
    """
    return estimate_fees()
