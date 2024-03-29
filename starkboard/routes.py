from flask import request, Blueprint
import os
from starkboard.transactions import transactions_in_block
from starkboard.contracts import count_contract_deployed_current_block
from starkboard.utils import StarkboardDatabase, Requester, require_appkey, generate_merkle_proof
from starkboard.fees import get_fees_in_block
from starkboard.user import whitelist, use_wallets_ranking
from starkboard.ecosystem.fetch_application import get_core_ecosystem
from datetime import date
from cache import cache

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/', methods=['GET'])
def landing():
    return 'ODA API'

wallets_1, leaves_1 = whitelist(StarkboardDatabase(), 0)
wallets_2, leaves_2 = whitelist(StarkboardDatabase(), 1)
wallets_3, leaves_3 = whitelist(StarkboardDatabase(), 2)

#######################
#    General Route    #
#######################

@app_routes.route('/storeNewsletter', methods=['POST'])
@require_appkey
def store_newsletter():
    """
    Stores an email address in the newsletter
    """
    try:
        data = request.get_json()
        starkboard_db = StarkboardDatabase()
        insert_res = starkboard_db.insert_newsletter(data)
        if insert_res:
            starkboard_db.close_connection()
            return {
                'result': f'Successfully inserted "{data["email_address"]}" in the newsletter'
            }, 200
        else:
            res = starkboard_db.get_newsletter(data)
            starkboard_db.close_connection()
            if not res:
                return {
                    'error': 'Insert in newsletter Error'
                }, 400
            else:
                return {
                    'result': res
                }, 200
    except Exception as e:
        print(e)
        return e, 400

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
        insert_res = starkboard_db.insert_starkboard_og(data)
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
    Gets an OG signature with its wallet address
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

@app_routes.route('/getWhitelistProof', methods=['POST'])
@require_appkey
def get_whitelist_proof():
    """
    Get whitelist proof given a wallet address
    """
    try:
        data = request.get_json()
        wl_type = data.get('wl_type', 0)
        wallet_address = int(data.get('wallet_address', ''), 16)
        proof = None
        if wl_type == 0:
            leave_number = wallets_1.index(wallet_address)
            proof = generate_merkle_proof(leaves_1, leave_number)
        elif wl_type == 1:
            leave_number = wallets_2.index(wallet_address)
            proof = generate_merkle_proof(leaves_2, leave_number)
        else:
            leave_number = wallets_3.index(wallet_address)
            proof = generate_merkle_proof(leaves_3, leave_number)
        if not proof:
            return {
                'error': 'User does not exists'
            }, 400
        else:
            proof = [str(pro) for pro in proof]
            return {
                'result': proof
            }, 200
    except ValueError as e:
        return {
            'error': str(e)
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


@app_routes.route('/getWalletRanking', methods=['POST'])
@require_appkey
def get_wallet_ranking():
    """
    Retrieve wallets ranking based on daily data
    """
    data = request.get_json()
    res = use_wallets_ranking(data.get('network'))
    return {
        'result': res
    }, 200


#######################
#  Global Data Route  #
#######################

@app_routes.route('/getDailyData', methods=['POST'])
@require_appkey
def get_daily_data():
    """
    Retrieve daily data
    """
    print(request.remote_addr)
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    if data.get('daily_only', False):
        res = starkboard_db.get_daily_data(data.get('day', date.today().strftime('%Y-%m-%d')))
    else:
        res = starkboard_db.get_historical_daily_data()
    starkboard_db.close_connection()
    return {
        'result': res
    }, 200


@app_routes.route('/getDailyTVLData', methods=['POST'])
@require_appkey
def get_daily_tvl_data():
    """
    Retrieve daily TVL data
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    res = starkboard_db.get_historical_tvl_data(data.get('token'))
    starkboard_db.close_connection()
    return {
        'result': res
    }, 200


@app_routes.route('/getDailyTransferData', methods=['POST'])
@require_appkey
def get_daily_transfer_data():
    """
    Retrieve daily Transfer data
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    res = starkboard_db.get_historical_transfer_data(data.get('token'))
    starkboard_db.close_connection()
    return {
        'result': res
    }, 200


@app_routes.route('/getCumulativeMetricEvolution', methods=['POST'])
@require_appkey
def get_cumulative_metric_evolution():
    """
    Retrieve a specific metric evolution over time
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    res = starkboard_db.get_cummulative_field_data(data.get('field'))
    starkboard_db.close_connection()
    return {
        'result': res
    }, 200


@app_routes.route('/getTokenTVLEvolution', methods=['POST'])
@require_appkey
def get_token_tvl_evolution():
    """
    Retrieve a specific token TVL evolution over time
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    res = starkboard_db.get_cummulative_tvl_data(data.get('token'))
    starkboard_db.close_connection()
    return {
        'result': res
    }, 200

@app_routes.route('/getCummulativeTransferVolumeEvolution', methods=['POST'])
@require_appkey
def get_cummulative_transfer_volume_evolution():
    """
    Retrieve a specific token transfer volume over time
    """
    data = request.get_json()
    starkboard_db = StarkboardDatabase(data.get('network'))
    res = starkboard_db.get_cummulative_transfer_volume_data(data.get('token'))
    starkboard_db.close_connection()
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
    """
    try:
        data = request.get_json()
        if data.get('network') == "mainnet":
            starknet_node = Requester(os.environ.get("STARKNET_NODE_URL_MAINNET"), headers={"Content-Type": "application/json"})
        else:
            starknet_node = Requester(os.environ.get("STARKNET_NODE_URL"), headers={"Content-Type": "application/json"})
        actual_fees =  get_fees_in_block(None, starknet_node)["mean_fees"]
        return {
            'result': actual_fees
        }, 200
    except Exception as e:
        return {
            'error': e.message
        }, 400


#######################
#   Events Routes     #
#######################

@app_routes.route('/getDailySwapEventsData', methods=['POST'])
@cache.cached(timeout=20)
@require_appkey
def get_daily_swap_events_data():
    """
    Retrieve the daily swaps events data
    """
    try:
        data = request.get_json()
        starkboard_db = StarkboardDatabase(data.get('network', 'testnet'))
        res = starkboard_db.get_historical_daily_swap_data(data.get('contract_address'))
        starkboard_db.close_connection()
        return {
            'result': res
        }, 200
    except Exception as e:
        return {
            'error': e.message
        }, 400

#######################
#  Ecosystem Route    #
#######################

@app_routes.route('/getCoreApplications', methods=['POST'])
@cache.cached(timeout=60)
@require_appkey
def get_core_application():
    """
    Retrieve the list of core application on StarkNet and its info
    """
    try:
        starkboard_db = StarkboardDatabase()
        list_core_applications = get_core_ecosystem(starkboard_db)
        starkboard_db.close_connection()
        return {
            'result': list_core_applications
        }, 200
    except Exception as e:
        return {
            'error': e.message
        }, 400
