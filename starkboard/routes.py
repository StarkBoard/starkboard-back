from imaplib import _Authenticator
import os
from flask import request, Blueprint
from starkboard.transactions import transactions_in_block
from starkboard.contracts import count_contract_deployed_current_block
from starkboard.utils import StarkboardDatabase, Requester, require_appkey
from starkboard.fees import get_block_fees
from datetime import date

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/', methods=['GET'])
def landing():
    return 'ODA API'


#######################
#    General Route    #
#######################
@app_routes.route('/storeStarkboardOg', methods=['POST'])
@require_appkey
def store_starkboard_og():
    """
    Stores a wallet OG with its signature
    """
    try:
        data = request.get_json()
        if "['" and "']"  not in data.get('signature'):
            return {
                "error": "Invalid Signature"
            }, 400
        starkboard_db = StarkboardDatabase()
        insert_res = starkboard_db.inserts_starkboard_og(data)
        if insert_res:
            starkboard_db.close_connection()
            return {
                'result': f'Successfully inserted OG {data["wallet_address"]}'
            }, 200
        else:
            res = starkboard_db.get_starkboard_og(data)
            starkboard_db.close_connection()
            if not res:
                return {
                    'error': 'Insert OG Error'
                }, 400
            else:
                return {
                    'result': res
                }, 200
    except Exception as e:
        print(e)
        return e, 400

@app_routes.route('/getStarkboardOg', methods=['POST'])
@require_appkey
def get_starkboard_og():
    """
    Stores a wallet OG with its signature
    """
    try:
        data = request.get_json()
        starkboard_db = StarkboardDatabase()
        res = starkboard_db.get_starkboard_og(data)
        starkboard_db.close_connection()
        if not res:
            return {
                'error': 'User does not exists'
            }, 400
        else:
            return {
                'result': res
            }, 200
    except Exception as e:
        return {
            'error': e.message
        }, 400

#######################
#    User Routes      #
#######################
@app_routes.route('/getWalletValue', methods=['POST'])
@require_appkey
def get_wallet_value():
    """
    Retrieve wallet value (ETH)
    TBD
    """
    return {}

#######################
#  Global Data Route  #
#######################
@app_routes.route('/getDailyData', methods=['POST'])
@require_appkey
def getDailyData():
    """
    Retrieve daily data
    TBD
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    if data.get('daily_only', False):
        res = starkboard_db.get_daily_data(data.get('day', date.today().strftime('%Y-%m-%d')))
    else:
        res = starkboard_db.get_historical_daily_data()
    return {
        'result': res
    }, 200


#######################
#  Contracts Routes   #
#######################
@app_routes.route('/getCurrentBlockCountContractsDeployed', methods=['GET'])
@require_appkey
def get_count_contrats_deployed_current_block():
    """
    Retrieve the number of Contract deployed on StarkNet on the latest block
    """
    data = request.get_json()
    if data.get('network', 'testnet') == "mainnet":
        staknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
        starknet_gateway = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL_MAINNET"), headers={"Content-Type": "application/json"})
    else:
        staknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        starknet_gateway = Requester(os.environ.get("STARKNET_FEEDER_GATEWAY_URL"), headers={"Content-Type": "application/json"})

    return count_contract_deployed_current_block(staknet_node, starknet_gateway)

@app_routes.route('/getMostUsedFunctionFromContract', methods=['GET'])
@require_appkey
def get_most_used_functions_from_contract():
    """
    Retrieve the most used functions of a Smart Contract with Count
    TBD
    """
    return {}


#######################
#    Fees Routes      #
#######################

@app_routes.route('/estimateFees', methods=['GET'])
@require_appkey
def get_estimate_fees():
    """
    Fees Estimation on the network
    TBD
    """
    try:
        data = request.get_json()
        if data.get('network') == "mainnet":
            starknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
        else:
            starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        actual_fees =  get_block_fees(4533, starknet_node)["mean_fees"]
        return {
            'res': actual_fees
        }, 200
    except Exception as e:
        return {
            'error': e.message
        }, 400
    