from starkboard.utils import StarkboardDatabase
from starkboard.ecosystem.fetch_application import update_core_ecosystem


if __name__ == '__main__':
    starkboard_db = StarkboardDatabase()
    update_core_ecosystem(starkboard_db)
