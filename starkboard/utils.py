import requests
import json
import os
import tweepy
from starkware.crypto.signature.fast_pedersen_hash import pedersen_hash
from flask import request, abort
from functools import wraps
from datetime import datetime, date
from threading import Timer
from db import get_connection

class Requester:
    """
    Custom API Request module
    """
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.session = requests.Session()
        for arg in kwargs:
            if isinstance(kwargs[arg], dict):
                kwargs[arg] = self.__deep_merge(getattr(self.session, arg), kwargs[arg])
            setattr(self.session, arg, kwargs[arg])
        self.base_request_data = {"jsonrpc":"2.0", "id":1, "method":"", "params":[]}
        
    def get_request_data(self, method, params):
        request_data = self.base_request_data
        request_data["method"] = method
        request_data["params"] = params
        return json.dumps(request_data)

    def request(self, method, url, **kwargs):
        return self.session.request(method, self.base_url+url, **kwargs)

    def head(self, url, **kwargs):
        return self.session.head(self.base_url+url, **kwargs)

    def get(self, url, **kwargs):
        return self.session.get(self.base_url+url, **kwargs)

    def post(self, url, method=None, params=None, **kwargs):
        if self.base_url == os.environ.get("STARKNET_NODE_URL") or self.base_url == os.environ.get('STARKNET_NODE_URL_MAINNET'):
            data = self.get_request_data(method, params)
        else:
            data = json.dumps(params)
        
        return self.session.post(self.base_url+url, data=data, **kwargs)

    def put(self, url, **kwargs):
        return self.session.put(self.base_url+url, **kwargs)

    def patch(self, url, **kwargs):
        return self.session.patch(self.base_url+url, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(self.base_url+url, **kwargs)

    @staticmethod
    def __deep_merge(source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                Requester.__deep_merge(value, node)
            else:
                destination[key] = value
        return destination

    def get_block_from_timestamp(self, timestamp):
        timestamp_data = {
            "operationName": "block_from_timestamp",
            "query": "query block_from_timestamp {block(where: {timestamp: {_gte: "+str(datetime.timestamp(timestamp) - 500)+", _lte: "+str(datetime.timestamp(timestamp) + 500)+"}}) {block_number, timestamp}}"
        }
        r = self.post("", method="", params=timestamp_data)    
        available_blocks = json.loads(r.text)["data"]["block"]    
        return available_blocks[len(available_blocks)//2]


class RepeatedTimer(object):
    """
    Automated timer to repeat function undefinitely each {interval} seconds
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.previous_run = True
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        if self.previous_run:
            self.previous_run = False
            self.previous_run = self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class StarkboardDatabase():
    """
    Starkboard MySQL Database handler
    """
    def __init__(self, newtork='testnet'):
        self.network = newtork
        if newtork == "mainnet":
            self._mainnet_suffix = "_mainnet"
        else:
            self._mainnet_suffix = ""
        self._connection = get_connection()

    def close_connection(self):
        self._connection.close()

    def execute_query(self, query):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()
            return cursor
        except Exception as e:
            print(e)
            return None

    #
    # Insertion Blocks and Daily
    #

    def insert_block_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""INSERT INTO block_data{self._mainnet_suffix}(
                    block_number, timestamp, full_day, count_txs, count_new_wallets, count_new_contracts, count_transfers, total_fees, mean_fees, wallets_active
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"""
            inserted_block = (data["block_number"], data["timestamp"], data["full_day"], data["count_txs"], 
                data["count_new_wallets"], data["count_new_contracts"], data["count_transfers"], data["total_fees"], data["mean_fees"], json.dumps(data["wallets_active"]))
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def update_block_data(self, block_number, count_transfer):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""UPDATE block_data{self._mainnet_suffix} SET count_transfers=%s WHERE block_number=%s;"""
            inserted_block = (count_transfer, block_number)
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            return False

    def update_block_fees(self, block_number, fees):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""UPDATE block_data{self._mainnet_suffix} SET total_fees=%s, mean_fees=%s WHERE block_number=%s;"""
            inserted_block = (fees.get('total_fees'), fees.get('mean_fees'), block_number)
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            return False

    def update_block_users(self, block_number, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""UPDATE block_data{self._mainnet_suffix} SET wallets_active=%s WHERE block_number=%s;"""
            inserted_block = (json.dumps(data.get('wallets_active')), block_number)
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            return False


    def insert_daily_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_upsert_query = f"""INSERT INTO daily_data{self._mainnet_suffix}(
                day, count_txs, count_new_wallets, count_new_contracts, count_transfers, total_fees, mean_fees, count_wallets_active, top_wallets_active
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE    
                day=%s, count_txs=%s, count_new_wallets=%s, count_new_contracts=%s, count_transfers=%s, total_fees=%s, mean_fees=%s, count_wallets_active=%s, top_wallets_active=%s
            """
            inserted_block = (
                data["day"], data["count_txs"], data["count_new_wallets"], data["count_new_contracts"], 
                data["count_transfers"], data["total_fees"], data["mean_fees"], data["count_wallets_active"], json.dumps(data["top_wallets_active"]),
                data["day"], data["count_txs"], data["count_new_wallets"], data["count_new_contracts"], 
                data["count_transfers"], data["total_fees"], data["mean_fees"], data["count_wallets_active"], json.dumps(data["top_wallets_active"])
            )
            cursor.execute(sql_upsert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def insert_daily_tvl_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_upsert_query = f"""INSERT INTO daily_mints{self._mainnet_suffix}(
                day, token, amount, avg_deposit, count_deposit, count_withdraw
                ) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE    
                day=%s, token=%s, amount=%s, avg_deposit=%s, count_deposit=%s, count_withdraw=%s
            """
            inserted_block = (
                data["day"], data["token"], 
                data["amount"], data["avg_deposit"], data["count_deposit"], data["count_withdraw"],
                data["day"], data["token"], 
                data["amount"], data["avg_deposit"], data["count_deposit"], data["count_withdraw"],
            )
            cursor.execute(sql_upsert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False


    def insert_daily_transfers_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_upsert_query = f"""INSERT INTO daily_transfers{self._mainnet_suffix}(
                day, token, amount, avg_transfer, count_transfer, max_transfer
                ) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE    
                day=%s, token=%s, amount=%s, avg_transfer=%s, count_transfer=%s, max_transfer=%s
            """
            inserted_block = (
                data["day"], data["token"], 
                data["amount"], data["avg_transfer"], data["count_transfer"], data["max_transfer"],
                data["day"], data["token"], 
                data["amount"], data["avg_transfer"], data["count_transfer"], data["max_transfer"],
            )
            cursor.execute(sql_upsert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    ##
    ## Insertion User data
    ##

    def inserts_starkboard_og(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = """INSERT INTO starkboard_og(
                    wallet_address, signature
                ) VALUES (%s,%s)"""
            inserted_block = (data["wallet_address"], data["signature"])
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def get_starkboard_og(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = """SELECT * FROM starkboard_og WHERE wallet_address=%s"""
            inserted_block = (data["wallet_address"])
            cursor.execute(sql_insert_query, inserted_block)
            res = cursor.fetchone()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    ##
    ## Insert Contracts
    ##

    def insert_contract_hash(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = """INSERT INTO contract_class(
                    class_hash, type, abi, event_names, event_keys, network
                ) VALUES (%s,%s,%s,%s,%s,%s)"""
            inserted_block = (data["class_hash"], data["type"], data["abi"], data["event_names"], data["event_keys"], self.network)
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def insert_contract_type(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = """INSERT INTO ecosystem_contracts(
                    contract_address, application, event_keys, contract_type, class_hash, abi, deployed_at, network
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            inserted_block = (
                data["contract_address"], data["application"], data["event_keys"], 
                data["type"], data["class_hash"], data['abi'], data['deployed_at'], self.network
            )
            cursor.execute(sql_insert_query, inserted_block)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    ##
    ## Insertion Ecosystem
    ##

    def insert_ecosystem_offchain(self, data):
        try:	
            cursor = self._connection.cursor()
            sql_insert_query = """INSERT INTO ecosystem(
                    application, application_short, isLive, isTestnetLive, 
                    github, medium, twitter, website,
                    discord, tags, countFollowers, description
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
                    application=%s, application_short=%s, isLive=%s, isTestnetLive=%s, 
                    github=%s, medium=%s, twitter=%s, website=%s,
                    discord=%s, tags=%s, countFollowers=%s, description=%s"""
            inserted_app = (
                data["application"], data["application_short"], 
                data["isLive"], data["isTestnetLive"],
                data["github"], data["medium"],
                data["twitter"], data["website"],
                data["discord"], data["tags"],
                data["countFollowers"], data["description"],
                data["application"], data["application_short"], 
                data["isLive"], data["isTestnetLive"],
                data["github"], data["medium"],
                data["twitter"], data["website"],
                data["discord"], data["tags"],
                data["countFollowers"], data["description"]
            )
            cursor.execute(sql_insert_query, inserted_app)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def update_ecosystem_twitter_social(self, data):
        try:	
            cursor = self._connection.cursor()
            sql_insert_query = """UPDATE ecosystem SET countFollowers=%s, countTweets=%s, profile_picture_url=%s WHERE application=%s;"""
            inserted_app = (
                data["followers_count"], data["tweet_count"], 
                data["profile_picture_url"], data["application"]
            )
            cursor.execute(sql_insert_query, inserted_app)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    ##
    ## Getters Ecosystem
    ##

    def get_ecosystem_offchain(self):
        try:	
            cursor = self._connection.cursor()
            sql_get_query = """SELECT * FROM ecosystem"""
            cursor.execute(sql_get_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    def get_ecosystem_twitter_handlers(self):
        try:	
            cursor = self._connection.cursor()
            sql_get_query = """SELECT application, twitter FROM ecosystem ORDER BY countFollowers DESC"""
            cursor.execute(sql_get_query)
            res = cursor.fetchall()
            res = [dict(app, twitter_handler=app.get('twitter').split('/')[-1]) for app in res]
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    ##
    ## Getters Contracts
    ##

    def get_contract_hash(self, class_hash):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = """SELECT * from contract_class WHERE class_hash=%s and network=%s"""
            inserted_block = (class_hash, self.network)
            cursor.execute(sql_insert_query, inserted_block)
            res = cursor.fetchone()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            self._connection = get_connection()
            return False

    ##
    ## Getters Blocks
    ##

    def get_checkpoint_block(self):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""SELECT block_number FROM block_data{self._mainnet_suffix} ORDER BY block_number DESC LIMIT 1"""
            cursor.execute(sql_insert_query)
            res = cursor.fetchone()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    ##
    ## Getters aggregated
    ##

    def get_daily_data_from_blocks(self):
        try:
            cursor = self._connection.cursor()
            cursor.execute("SET SESSION group_concat_max_len = 10000000;")
            sql_select_query = f"""SELECT full_day as day, SUM(count_txs) as count_txs, 
                SUM(count_transfers) as count_transfers,
                SUM(count_new_wallets) as count_new_wallets,
                SUM(count_new_contracts) as count_new_contracts,
                SUM(total_fees) as total_fees,
                SUM(total_fees) / SUM(count_txs) as mean_fees,
                GROUP_CONCAT(wallets_active SEPARATOR ',') as list_wallets_active
                FROM block_data{self._mainnet_suffix}
                GROUP BY full_day
                ORDER BY full_day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_wallets_info_blocks(self):
        try:
            cursor = self._connection.cursor()
            cursor.execute("SET SESSION group_concat_max_len = 10000000;")
            sql_select_query = f"""SELECT full_day as day,
                GROUP_CONCAT(wallets_active SEPARATOR ',') as list_wallets_active
                FROM block_data{self._mainnet_suffix}
                WHERE full_day between DATE_SUB(now(),INTERVAL 4 WEEK) and now()
                GROUP BY full_day
                ORDER BY full_day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    ##
    ## Delete Blocks
    ##

    def delete_old_block_data(self, date):
        try:
            cursor = self._connection.cursor()
            sql_delete_query = f"""DELETE FROM block_data{self._mainnet_suffix}
                WHERE full_day < '{date}'"""
            cursor.execute(sql_delete_query)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            return False

    ##
    ## ERC-20 Getters
    ##

    def get_daily_tvl_data_from_blocks(self):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT fullDay as day, token,
                SUM(CASE WHEN type = 'deposit' THEN value ELSE -value END) as amount,
                SUM(CASE WHEN type = 'deposit' THEN 1 ELSE 0 END) as count_deposit,
                SUM(CASE WHEN type = 'deposit' THEN 0 ELSE 1 END) as count_withdraw
                FROM mints{self._mainnet_suffix}
                GROUP BY fullDay, token
                ORDER BY fullDay DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_daily_average_deposit_data_from_blocks(self):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT fullDay as day, token,
                AVG(value) as avg_deposit
                FROM mints{self._mainnet_suffix}
                WHERE type = 'deposit'
                GROUP BY fullDay, token
                ORDER BY fullDay DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_daily_transfer_data_from_blocks(self):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT fullDay as day, token,
                SUM(value) as amount,
                AVG(value) as avg_transfer,
                COUNT(*) as count_transfer,
                MAX(value) as max_transfer
                FROM transfers{self._mainnet_suffix}
                GROUP BY fullDay, token
                ORDER BY fullDay DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    ###
    ### API Getters
    ###

    def get_daily_data(self, date=date.today().strftime('%Y-%m-%d')):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT *
                FROM daily_data{self._mainnet_suffix}
                WHERE day = '{date}'
                ORDER BY day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchone()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_historical_daily_data(self):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT *
                FROM daily_data{self._mainnet_suffix}
                ORDER BY day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_historical_tvl_data(self, token):
        try:
            cursor = self._connection.cursor()
            if token:
                sql_select_query = f"""SELECT *
                    FROM daily_mints{self._mainnet_suffix}
                    WHERE token = '{token}'
                    ORDER BY day DESC"""
            else:
                sql_select_query = f"""SELECT *
                    FROM daily_mints{self._mainnet_suffix}
                    ORDER BY day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_historical_transfer_data(self, token):
        try:
            cursor = self._connection.cursor()
            if token:
                sql_select_query = f"""SELECT *
                    FROM daily_transfers{self._mainnet_suffix}
                    WHERE token = '{token}'
                    ORDER BY day DESC"""
            else:
                sql_select_query = f"""SELECT *
                    FROM daily_transfers{self._mainnet_suffix}
                    ORDER BY day DESC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_cummulative_tvl_data(self, token="ETH"):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT t.day, (
                    SELECT SUM(amount) 
                    FROM daily_mints{self._mainnet_suffix} t2
                    WHERE t2.day <= t.day and t2.token = '{token}'
                ) as aggregated_amount, t.token
                FROM daily_mints{self._mainnet_suffix} t
                WHERE t.token = '{token}'
                ORDER BY t.day ASC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_cummulative_transfer_volume_data(self, token="ETH"):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT t.day, (
                    SELECT SUM(amount) 
                    FROM daily_transfers{self._mainnet_suffix} t2
                    WHERE t2.day <= t.day and t2.token = '{token}'
                ) as aggregated_amount, t.token
                FROM daily_transfers{self._mainnet_suffix} t
                WHERE t.token = '{token}'
                ORDER BY t.day ASC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False

    def get_cummulative_field_data(self, field="count_txs"):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT t.day, (
                    SELECT SUM({field}) 
                    FROM daily_data{self._mainnet_suffix} t2
                    WHERE t2.day <= t.day
                ) as aggregated_amount
                FROM daily_data{self._mainnet_suffix} t
                ORDER BY t.day ASC"""
            cursor.execute(sql_select_query)
            res = cursor.fetchall()
            self._connection.commit()
            cursor.close()
            return res
        except Exception as e:
            print(e)
            return False


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == os.environ.get('API_KEY'):
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


def generate_merkle_root(values):
    if len(values) == 1:
        return values[0]

    if len(values) % 2 != 0:
        values.append(0)

    next_level = get_next_level(values)
    return generate_merkle_root(next_level)

# generates merkle proof from an index of the value list
# each pair of values must be in sorted order
def generate_merkle_proof(values, index):
    return generate_proof_helper(values, index, [])

# checks the validity of a merkle proof
# the last element of the proof should be the root
def verify_merkle_proof(leaf, proof):
    root = proof[len(proof)-1]
    proof = proof[:-1]
    curr = leaf

    for proof_elem in proof:
        if curr < proof_elem:
            curr = pedersen_hash(curr, proof_elem)
        else:
            curr = pedersen_hash(proof_elem, curr)

    return curr == root

# gets the leaf node for a particular merkle distributor claim
def get_leaf(recipient, amount):
    amount_hash = pedersen_hash(amount, 0)
    leaf = pedersen_hash(recipient, amount_hash)
    return leaf

# creates the inital merkle leaf values to use
def get_leaves(recipients, amounts):
    values = []
    for i in range(0, len(recipients)):
        leaf = get_leaf(recipients[i], amounts[i])
        value = (leaf, recipients[i], amounts[i])
        values.append(value)

    if len(values) % 2 != 0:
        last_value = (0, 0, 0)
        values.append(last_value)

    return values

def get_next_level(level):
    next_level = []

    for i in range(0, len(level), 2):
        node = 0
        if level[i] < level[i+1]:
            node = pedersen_hash(level[i], level[i+1])
        else:
            node = pedersen_hash(level[i+1], level[i])

        next_level.append(node)

    return next_level

def generate_proof_helper(level, index, proof):
    if len(level) == 1:
        return proof
    if len(level) % 2 != 0:
        level.append(0)

    next_level = get_next_level(level)
    index_parent = 0

    for i in range(0, len(level)):
        if i == index:
            index_parent = i // 2
            if i % 2 == 0:
                proof.append(level[index+1])
            else:
                proof.append(level[index-1])

    return generate_proof_helper(next_level, index_parent, proof)
