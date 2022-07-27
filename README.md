# StarkBoard API

On and Off chain data of StarkNet within a single Flask API

## Installation Setup

- Python >=3.8


```
python -m venv starkboard-env
source starkboard-env/bin/activate
pip install --upgrade pips
pip install -r requirements.txt
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