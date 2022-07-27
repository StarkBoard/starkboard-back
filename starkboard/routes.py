from app import app
from starkboard.transactions import get_transactions

@app.route('/', methods=['GET'])
def landing():
    return 'ODA API'

#######################
# Transactions Routes #
#######################

@app.route('/tx', methods=['GET'])
def transactions():
    return get_transactions()
