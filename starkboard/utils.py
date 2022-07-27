import requests
import json
import os
from datetime import datetime, time, timedelta


class Requester:
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