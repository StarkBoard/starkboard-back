from imaplib import _Authenticator
from flask import request, Blueprint
from starkboard.transactions import transactions_in_block
from starkboard.contracts import count_contract_deployed_current_block
from starkboard.utils import StarkboardDatabase, require_appkey
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
        starkboard_db.close_connection()
        if insert_res:
            return {
                'result': f'Successfully inserted OG {data["wallet_address"]}'
            }, 200
        else:
            return {
                'error': f'OG {data["wallet_address"]} already registered'
            }, 400
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
    starkboard_db = StarkboardDatabase()
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
    return count_contract_deployed_current_block()

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

@app_routes.route('/estimateFee', methods=['GET'])
@require_appkey
def get_estimate_fees():
    """
    Fees Estimation on the network
    TBD
    """
    return {}
