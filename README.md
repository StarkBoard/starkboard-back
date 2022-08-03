# StarkBoard API

On and Off chain data of StarkNet within a single Flask API

## Installation Setup

- Python >=3.8


```
python -m venv starkboard-env
source starkboard-env/bin/activate
pip install --upgrade pips
CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib pip install -r requirements.txt
```

## Scripts

- Fetching and archiving Transactions count for block 
```
python fetcher.py -t True --fromBlock 260000 --toBlock 265000
```

- Fetching and archiving Block data from block
```
python fetcher.py -b True --fromBlock 254000 
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

## Documentation

- `/store_starkboard_og` [POST]
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


- `/get_starkboard_og` [POST]
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
    "signature": "Signed By Exo",
    "user_rank": 4,
    "wallet_address": "0x0586f215eEAFcA7340A4Ef0D7Cbb9310Ee99122dE3C47f24Cc788F4AeB2f8d9C"
}
```