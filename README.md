# StarkBoard API

On and Off chain data of StarkNet within a single Flask API

## Installation Setup

- Python >=3.8


```
python -m venv starkboard-env
source starkboard-env/bin/activate
pip install --upgrade pip
CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib pip install -r requirements.txt
```

## Scripts

- Fetching and archiving Block data from block
```
python fetcher.py -b True -n testnet
python fetcher.py -b True -n mainnet
```

- Insert final Daily data
```
python etl.py
```



## Launch API

- Development
```
FLASK_ENV=development flask run
```

- Production
```
FLASK_ENV=production flask run
```

- AWS Deployment
```
eb deploy
```

## Documentation

Route returing error will always return a dict : 
```
{
    'error': 'err msg'
}
```

- `/storeStarkboardOg` [POST]
Store an OG to StarkBoard Database

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| wallet_address  |   String: OG Wallet to store     |
| signature  |   Signature to store      |

3. Return

```
{
    'result': 'Successfully inserted OG 0x0586f215eEAFcA7340A4Ef0D7Cbb9310Ee99122dE3C47f24Cc788F4AeB2f8d9C'
}
```


- `/getStarkboardOg` [POST]
Retrieve a OG to StarkBoard Database

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| wallet_address  |   String: OG Wallet to retrieve     |

3. Return

```
{
    'result': {
        "signature": "Signed By Exo",
        "user_rank": 4,
        "wallet_address": "0x0586f215eEAFcA7340A4Ef0D7Cbb9310Ee99122dE3C47f24Cc788F4AeB2f8d9C"
    }
}
```


- `/getDailyData` [POST]
Retrieve daily basic data of StarkNet Onchain dat

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| only_daily  |   Bool: if false, retrieve historical data from first day    |
| day  |   String: Day to retrieve, today if not provided ('2022-01-31')    |
| network  |   String: Network to target (mainnet, testnet)    |


3. Return

```
{
    'result': [
        {
            "mean_fees": 0.13,
            "total_fees": 1.3223,
            "count_new_contracts": 1455,
            "count_new_wallets": 1009,
            "count_transfers": 0,
            "count_txs": 11438,
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```

- `/getDailyTVLData` [POST]
Retrieve daily TVL data (organized by tokens) of StarkNet Onchain dat

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |
| token  |   String: Optionnal, specific token data to filter on  |


3. Return

```
{
    'result': [
        {
            "count_deposit": 10,
            "count_withdraw": 2,
            "avg_deposit": 0.23,
            "amount": 213,
            "token": "ETH",
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```



- `/getDailyTransferData` [POST]
Retrieve daily Transfers data (organized by tokens) of StarkNet Onchain dat

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |
| token  |   String: Optionnal, specific token data to filter on  |


3. Return

```
{
    'result': [
        {
            "top_wallet": "0x",
            "max_transfer": 10,
            "count_transfer": 2,
            "avg_transfer": 0.23,
            "amount": 213,
            "token": "ETH",
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```
