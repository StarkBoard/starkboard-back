from starkboard.utils import StarkboardDatabase, get_twitter_api_auth, get_application_follower
from starkboard.ecosystem.fetch_application import update_core_ecosystem, get_core_ecosystem
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    starkboard_db = StarkboardDatabase()
    get_core_ecosystem(starkboard_db)
    twitter_api = get_twitter_api_auth()
    get_application_follower("Starkboard", twitter_api)
