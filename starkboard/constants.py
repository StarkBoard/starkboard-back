#################################
#        Available   Keys       #
#################################

TRANSACTION_EXECUTED_KEY = ["0x5ad857f66a5b55f1301ff1ed7e098ac6d4433148f0b72ebc4a2945ab85ad53"]
APPROVAL_KEY = ["0x134692b230b9e1ffa39098904722134159652b09c5bc41d88d6698779d228ff"]
APPROVALFORALL_KEY = ["0x6ad9ed7b6318f1bcffefe19df9aeb40d22c36bed567e1925a5ccde0536edd"]
TRANSFER_KEY = ["0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9"]
TRANSFERBATCH_KEY = ["0x2563683c757f3abe19c4b7237e2285d8993417ddffe0b54a19eb212ea574b08"]
SWAP_KEY = ["0xe316f0d9d2a3affa97de1d99bb2aac0538e2666d0d8545545ead241ef0ccab"]
MINT_KEY = ["0x34e55c1cd55f1338241b50d352f0e91c7e4ffad0e4271d64eb347589ebdfd16"]
BURN_KEY = ["0x243e1de00e8a6bc1dfa3e950e6ade24c52e4a25de4dee7fb5affe918ad1e744"]
SYNC_KEY = ["0xe14a408baf7f453312eec68e9b7gd728ec5337fbdf671f917ee8c80f3255232"]
PAIRCREATED_KEY = ["0x19437bf1c5c394fc8509a2e38c9c72c152df0bac8be777d4fc8f959ac817189"]
DEPOSIT_KEY = ["0x9149d2123147c5f43d258257fef0b7b969db78269369ebcf5ebb9eef8592f2"]
WITHDRAW_KEY = ["0x17f87ab38a7f75a63dc465e10aadacecfca64c44ca774040b039bfb004e3367"]

LIST_EVENT_KEYS = {
    "Transaction": TRANSACTION_EXECUTED_KEY,
    "Approval": APPROVAL_KEY,
    "ApprovalForAll": APPROVALFORALL_KEY,
    "Transfer": TRANSFER_KEY,
    "TransferBatch": TRANSFERBATCH_KEY,
    "Swap": SWAP_KEY,
    "Mint": MINT_KEY,
    "Burn": BURN_KEY,
    "Sync": SYNC_KEY,
    "PairCreated": PAIRCREATED_KEY,
    "Deposit": DEPOSIT_KEY,
    "Withdraw": WITHDRAW_KEY
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

ERC20_STD = {
    "functions": ["name", "symbol", "decimals", "balanceOf", "totalSupply", "approve", "transfer"], 
    "name": "ERC20",
    "event_names": ["Transfer", "Approval"]
}
ERC20_LP_STD = {
    "functions": ["name", "symbol", "decimals", "transfer", "approve"], 
    "name": "ERC20-LP",
    "event_names": ["Transfer", "Approval", "Swap"]
}
ERC721_STD = {
    "functions": ["name", "symbol", "tokenURI", "approve", "ownerOf"], 
    "name": "ERC721",
    "event_names": ["Transfer", "Approval"],
}
ERC1155_STD = {
    "functions": ["balanceOf", "balanceOfBatch"],
    "name": "ERC1155",
    "event_names": ["TransferBatch", "ApprovalForAll"]
}
ERC4626_STD = {
    "functions": ["deposit", "withdraw"],
    "name": "ERC4626",
    "event_names": ["Deposit",  "Withdraw"]
}
ACCOUNT_STD = {
    "functions": ["__execute__", "supportsInterface"], 
    "name": "Account",
    "event_names": []
}
ROUTER_STD = {
    "functions": ["Router", "swap"], 
    "name": "Router",
    "event_names": []
}

CONTRACT_STANDARDS = [ERC20_LP_STD, ERC4626_STD, ERC20_STD, ERC1155_STD, ERC721_STD, ACCOUNT_STD, ROUTER_STD]

CLASS_HASH_TYPE = {
    "ERC20": ERC20_STD,
    "ERC20-LP": ERC20_LP_STD,
    "Router": ROUTER_STD,
    "ERC721": ERC721_STD,
    "ERC1155": ERC1155_STD,
    "ERC5626": ERC4626_STD,
    "Account": ACCOUNT_STD
}

APP_NAME = {
    "ERC20-LP-JediSwap": "JediSwap"
}
