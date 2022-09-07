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

(Catcher):
```
python catcher.py -b True -n testnet
python catcher.py -t True -n testnet --fromBlock 296514 --toBlock 300000
python catcher.py -f True -n mainnet --fromBlock 0 --toBlock 100
python catcher.py -u True -n mainnet --fromBlock 0 --toBlock 100
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

### Mint / NFT / Users


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

- `/getWhitelistProof` [POST]
Retrieve a proof given a merkle root and a wallet address

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| wallet_address  |   String: Wallet address to retrieve proof for    |
| wl_type  |   Integer: 0, 1 or 2 depending on the whitelist status : 0 is top 2000, 1 is if missing next 3000, 2 is random 1000  |


3. Return

```
{
    'result': [
        "XXX",
        "XXX,
        ...
    ]
}
```


### Data


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


- `/getCumulativeMetricEvolution` [POST]
Retrieve a specific metric evolution over time

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |
| field  |   String: Field to retrieve data on (one of : 'count_txs', 'count_new_wallets', 'count_contracts_deployed', 'count_transfers', 'total_fees')  |


3. Return

```
{
    'result': [
        {
            "aggregated_amount": 100,
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```



- `/getTokenTVLEvolution` [POST]
Retrieve a specific token TVL evolution over time

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |
| token  |   String: Token ERC20 to retrieve data on (one of : 'ETH', 'DAI', 'WBTC', 'USDT', 'USDC', 'STARK')  |


3. Return

```
{
    'result': [
        {
            "aggregated_amount": 100,
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```


- `/getCummulativeTransferVolumeEvolution` [POST]
Retrieve a specific token transfer volume evolution over time

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |
| token  |   String: Token ERC20 to retrieve data on (one of : 'ETH', 'DAI', 'WBTC', 'USDT', 'USDC', 'STARK')  |


3. Return

```
{
    'result': [
        {
            "aggregated_amount": 1237,
            "day": "Thu, 04 Aug 2022 00:00:00 GMT"
        }
    ]
}
```


- `/getWalletRanking` [POST]
Retrieve Wallet Ranking (monthly) by number of TXs (most active)

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|
| network  |   String: Network to target (mainnet, testnet)    |


3. Return

```
{
    'result': [
        {
            "count_txs": 0,
            "eth": 0.0,
            "wallet_address": "0x7c57808b9cea7130c44aab2f8ca6147b04408943b48c6d8c3c83eb8cfdd8c0b",
            "weekly_tx": 236
        },
        ...
    ]
}
```




- `/getCoreApplications` [POST]
Retrieve lyst of Ecosystem Starknet applications

1. Headers

| Key  | Value          |
| :--------------- |:---------------:|
| Content-Type  |   application/json      |
| Accept  |   application/json      |

2. Data (JSON)

| Key  | Value          |
| :--------------- |:---------------:|


3. Return

```
{
    'result': [
        {
            "application": "AlmanacNFT",
            "application_short": "almanac",
            "countFollowers": 0,
            "description": "AlmanacNFT is a collection of 10.000 unique crypto trading days. Just pick a market, pick a date, and mint a day in crypto.",
            "discord": "",
            "github": "https://github.com/grillolepic/almanacNFT_cairo",
            "isLive": 1,
            "isTestnetLive": 0,
            "medium": "",
            "tags": "[\"nft\"]",
            "twitter": "https://twitter.com/almanacNFT",
            "website": "https://almanacNFT.xyz/"
        },
        ...
    ]
}
```
