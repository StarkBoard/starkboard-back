from imaplib import _Authenticator
from app import app
from flask import request
from starkboard.transactions import transactions_in_block
from starkboard.fees import estimate_fees
from starkboard.user import count_wallet_deployed
from starkboard.contracts import count_contract_deployed, most_used_functions_from_contract

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
#    User Routes      #
#######################
@app.route('/getCountWalletDeployed', methods=['GET'])
def get_count_wallet_deployed():
    """
    Retrieve the daily number of Wallets deployed (ArgentX or Braavos or All)
    """
    wallet_type = request.args.get('walletType')
    return count_wallet_deployed(wallet_type)


#######################
#  Contracts Routes   #
#######################
@app.route('/getCountContractsDeployed', methods=['GET'])
def get_count_contrats_deployed():
    """
    Retrieve the daily number of Contract deployed on StarkNet
    """
    return count_contract_deployed()

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
