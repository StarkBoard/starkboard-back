#################################
#        Available   Keys       #
#################################

TRANSACTION_EXECUTED_KEY = ["0x5ad857f66a5b55f1301ff1ed7e098ac6d4433148f0b72ebc4a2945ab85ad53"]
APPROVAL_KEY = ["0x134692b230b9e1ffa39098904722134159652b09c5bc41d88d6698779d228ff"]
TRANSFER_KEY = ["0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"]
SWAP_KEY = ["0xe316f0d9d2a3affa97de1d99bb2aac0538e2666d0d8545545ead241ef0ccab"]
MINT_KEY = ["0x34e55c1cd55f1338241b50d352f0e91c7e4ffad0e4271d64eb347589ebdfd16"]
BURN_KEY = ["0x243e1de00e8a6bc1dfa3e950e6ade24c52e4a25de4dee7fb5affe918ad1e744"]
SYNC_KEY = ["0xe14a408baf7f453312eec68e9b7d728ec5337fbdf671f917ee8c80f3255232"]
PAIRCREATED_KEY = ["0x19437bf1c5c394fc8509a2e38c9c72c152df0bac8be777d4fc8f959ac817189"]

LIST_EVENT_KEYS = {
    "Transaction": TRANSACTION_EXECUTED_KEY,
    "Approval": APPROVAL_KEY,
    "Transfer": TRANSFER_KEY,
    "Swap": SWAP_KEY,
    "Mint": MINT_KEY,
    "Burn": BURN_KEY,
    "Sync": SYNC_KEY,
    "PairCreated": PAIRCREATED_KEY
}

#################################
#     Available Wallets Keys    #
#################################

WALLET_KEYS = {
    "ArgentX": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784"],
    "Braavos": ["0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"],
    "All": ["0x10c19bef19acd19b2c9f4caa40fd47c9fbe1d9f91324d44dcd36be2dae96784", "0x17edf1120040be1bbc6931f143df1cc1cf80bb7f7fdadb251a3668ba3755049"]
}

#################################
#  Available Standard Contrats  #
#################################

ERC20_STD = [
    ["name", "symbol", "decimals", "balanceOf", "totalSupply", "approve", "Transfer"], 
    "ERC20",
    [LIST_EVENT_KEYS["Transfer"], LIST_EVENT_KEYS["Approval"], LIST_EVENT_KEYS["Mint"], LIST_EVENT_KEYS["Burn"]]
]
ERC20_LP_STD = [
    ["name", "symbol", "totalSupply", "Approval", "Transfer", "Swap"], 
    "ERC20-LP",
    [LIST_EVENT_KEYS["Transfer"], LIST_EVENT_KEYS["Approval"], LIST_EVENT_KEYS["Mint"], LIST_EVENT_KEYS["Burn"], LIST_EVENT_KEYS["Swap"]]
]
ERC721_STD = [
    ["name", "symbol", "tokenURI", "approve", "ownerOf"], 
    "ERC721",
    [LIST_EVENT_KEYS["Transfer"], LIST_EVENT_KEYS["Approval"], LIST_EVENT_KEYS["Mint"], LIST_EVENT_KEYS["Burn"]],
]
ERC1155_STD = [
    ["balanceOf", "balanceOfBatch"],
    "ERC1155",
    [LIST_EVENT_KEYS["Transfer"], LIST_EVENT_KEYS["Approval"], LIST_EVENT_KEYS["Mint"], LIST_EVENT_KEYS["Burn"]]
]
ACCOUNT_STD = [
    ["__execute__", "supportsInterface"], 
    "Account",
    [LIST_EVENT_KEYS["Transfer"]]
]
ROUTER_STD = [
    ["Router", "swap"], 
    "Router",
    []
]

EVENT_KEYS = [ERC20_LP_STD, ERC20_STD, ERC1155_STD, ERC721_STD, ACCOUNT_STD, ROUTER_STD]

CLASS_HASH_TYPE = {
    "ERC20": ERC20_STD,
    "ERC20-LP": ERC20_LP_STD,
    "Router": ROUTER_STD,
    "ERC721": ERC721_STD,
    "ERC1155": ERC1155_STD,
    "Account": ACCOUNT_STD
}

APP_NAME = {
    "ERC20-LP-JediSwap": "JediSwap"
}
