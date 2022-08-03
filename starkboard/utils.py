import requests
import json
import os
from datetime import datetime, time, timedelta
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
        if self.base_url == os.environ.get("STARKNET_NODE_URL"):
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
    def __init__(self):
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
            sql_insert_query = """INSERT INTO block_data(
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