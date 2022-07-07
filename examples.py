import json
import re
from operator import itemgetter
from os import path
from time import sleep
import schedule

from requests_html import HTMLSession
# from web3 import Web3

# https://web3py.readthedocs.io/en/stable/web3.main.html


class ChainsData:
    def __init__(self):
        self.s = HTMLSession()
        self.tvl_refresh_count = 0
        self.tx_refresh_count = 0
        

    def variation(self, new, old):
        """Compute a % change"""
        return round((new - old) / old * 100, 2)
    
    ########################################################################################################################
    
    def fetch_tvls(self):
        """Updating TVL file"""
        with open("files/tvls.json", "w") as file:
            res = self.s.get("https://api.llama.fi/chains").json()
            json.dump(dict([(c["name"], round(c["tvl"], 2)) for c in res if c["tvl"] > 0]), file)
        print("Chain's TVL file created.")
    
    def fetch_tx_number(self):
        """Function to get the Tx number of a chain
        using scraping / api"""
        
        explorers = {
        "ethereum": "https://etherscan.io/",
        "avalanche": "https://snowtrace.io/",
        "fantom": "https://ftmscan.com/",
        "polygon": "https://polygonscan.com/",
        "arbitrum": "https://arbiscan.io/",
        "optimism": "https://optimistic.etherscan.io/",
        "bsc": "https://bscscan.com/",
        "metis": "https://andromeda-explorer.metis.io/",
        "solana": ""
    }
        
        tx_number = dict()
        for chain in explorers:
            if chain == "metis":
                r = self.s.get(f"{explorers[chain]}")
                number = r.html.xpath('/html/body/div[1]/main/div/div/div/div[3]/div/div[2]/div/span')[0].text
                tx_number[chain] = int(number.replace(",", "").replace(",", ""))
                continue
            
            if chain == "solana":
                json_data = {
                        'method': 'getEpochInfo',
                        'jsonrpc': '2.0',
                        'params': [],
                        'id': 'e013e367-b20a-40f7-b742-6f7636f28029',
                    }

                r = self.s.post('https://explorer-api.mainnet-beta.solana.com/', json=json_data).json()
                number = r['result']['transactionCount']
                tx_number[chain] = number
                continue
            
            
            r = self.s.get(f"{explorers[chain]}txs")
            element = r.html.xpath('//*[@id="ContentPlaceHolder1_topPageDiv"]/p/span[1]/text()')
            number = re.findall(r'[\d]+[.,\d]+', " ".join(element))[0]
            
            tx_number[chain] = int(number.replace(",", "").replace(" ", ""))
        
        return tx_number
    
    ########################################################################################################################
    
    def tvl_gainer(self):
        """Fetching TVL evolution of chains"""
                
        if not path.exists("files/tvls.json"):                
            return self.fetch_tvls()
        
        # Getting old TVL data
        with open("files/tvls.json") as file:
            old_data = json.load(file)
    
        # Fetching fresh data (chain, TVL)
        res = self.s.get("https://api.llama.fi/chains").json()
        new_data = dict([(c["name"], round(c["tvl"], 2)) for c in res if c["name"] in old_data])
                
        # Comparing (applying variation func to each chain then sorting result)
        changes = dict([(chain, self.variation(old_data[chain], new_data[chain])) for chain in new_data])
        
        sorted_changes = sorted(changes.items(), key=itemgetter(1), reverse=True)
        
        with open("tvls_evolution.json", "w") as file:
            json.dump(dict(sorted_changes), file)
        
        print("tvls_evolution.json updated.")
        self.tvl_refresh_count += 1
        
        if self.tvl_refresh_count == 7:
            self.fetch_tvls()
            self.tvl_refresh_count = 0


    def compare_tx_number(self):
        
        if not path.exists("files/chains_tx.json"):
            with open("files/chains_tx.json", "w") as file:
                json.dump(self.fetch_tx_number(), file)
            print("Transactions count file created.")
            return
            
            
        with open("files/chains_tx.json") as file:
            old_data = json.load(file)
        
        new_data = self.fetch_tx_number()
        
        # Comparing (applying variation func to each chain then sorting result)
        try:
            changes = dict([(chain, self.variation(new_data[chain], old_data[chain])) for chain in new_data])
        except Exception:
            if retry_count < 4:
                print("Error, next try in 10 seconds.")
                sleep(10)
                self.compare_tx_number()
                retry_count += 1
        
        sorted_changes = dict(sorted(changes.items(), key=itemgetter(1), reverse=True))
        
        with open("tx_changes.json", "w") as file:
            json.dump(sorted_changes, file)
        
        self.tx_refresh_count += 1
        print("Transactions changes file updated.")
        
        if self.tx_refresh_count == 7:
            with open("files/chains_tx.json", "w") as file:
                json.dump(new_data, file)
            
            print("Transactions old data updated.")
            self.tx_refresh_count = 0
        

    def run(self):
        self.tvl_gainer()
        self.compare_tx_number()


data = ChainsData()

# data.run()


# schedule.every(24).hours.do(data.run)

# while True:
#     schedule.run_pending()
#     sleep(1)
