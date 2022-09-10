from starkboard.utils import StarkboardDatabase, get_twitter_api_auth, get_application_follower
from starkboard.ecosystem.fetch_application import update_core_ecosystem
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    starkboard_db = StarkboardDatabase()
    list_ecosystem = starkboard_db.get_ecosystem_twitter_handlers()
    twitter_api = get_twitter_api_auth()
    for app in list_ecosystem:
        print(app.get('twitter'))
