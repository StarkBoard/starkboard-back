from web3 import Web3


web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/INFURA_KEY'))

wei_bridge_balance = web3.eth.get_balance("0xae0Ee0A63A2cE6BaeEFFE56e7714FB4EFE48D419")

eth_bridge_balance = round(web3.fromWei(wei_bridge_balance, "ether"), 2)

print(eth_bridge_balance)

# >>> 429.45
