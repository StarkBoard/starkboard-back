import os
import argparse
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import RepeatedTimer, StarkboardDatabase, Requester, chunks
from starkboard.transactions import transactions_in_block, get_transfer_transactions_in_block, get_transfer_transactions, get_transfer_transactions_v2, get_transfer_transactions_in_block_v2
from starkboard.user import count_wallet_deployed, get_wallet_address_deployed, get_active_wallets_in_block
from starkboard.contracts import count_contract_deployed_in_block
from starkboard.tokens import get_eth_total_supply, get_balance_of
from starkboard.fees import get_block_fees
import signal
import asyncio
from datetime import datetime
import time


def monitor():




    return 


if __name__ == '__main__':
    monitor()
