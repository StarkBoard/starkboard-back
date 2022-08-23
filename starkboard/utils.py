import requests
import json
import os
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
            return True
        except Exception as e:
            print(e)
            return False

    def insert_block_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_insert_query = f"""INSERT INTO block_data{self._mainnet_suffix}(
                    block_number, timestamp, full_day, count_txs, count_new_wallets, count_new_contracts, count_transfers
                ) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            inserted_block = (data["block_number"], data["timestamp"], data["full_day"], data["count_txs"], 
                data["count_new_wallets"], data["count_new_contracts"], data["count_transfers"])
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

    def get_daily_data_from_blocks(self):
        try:
            cursor = self._connection.cursor()
            sql_select_query = f"""SELECT full_day as day, SUM(count_txs) as count_txs, 
                SUM(count_transfers) as count_transfers,
                SUM(count_new_wallets) as count_new_wallets,
                SUM(count_new_contracts) as count_new_contracts
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

    ##
    ## Insertors
    ##

    def insert_daily_data(self, data):
        try:
            cursor = self._connection.cursor()
            sql_upsert_query = f"""INSERT INTO daily_data{self._mainnet_suffix}(
                day, count_txs, count_new_wallets, count_new_contracts, count_transfers
                ) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE    
                day=%s, count_txs=%s, count_new_wallets=%s, count_new_contracts=%s, count_transfers=%s
            """
            inserted_block = (
                data["day"], data["count_txs"], 
                data["count_new_wallets"], data["count_new_contracts"], data["count_transfers"],
                data["day"], data["count_txs"], 
                data["count_new_wallets"], data["count_new_contracts"], data["count_transfers"]
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
