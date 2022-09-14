from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import Requester, StarkboardDatabase, get_twitter_api_auth, get_application_follower


def socials_metrics():
    starkboard_db = StarkboardDatabase()
    list_ecosystem = starkboard_db.get_ecosystem_twitter_handlers()
    twitter_api = get_twitter_api_auth()
    for app in list_ecosystem:
        if app.get("twitter_handler"):
            public_metrics = get_application_follower(app.get("twitter_handler"), twitter_api)
            if not public_metrics:
                continue
            print(f'Retrieved Social metrics for {app.get("twitter_handler")}')
            print(public_metrics)
            updated_data = {
                "application": app.get("application"),
                "followers_count": public_metrics.get("followers_count"),
                "tweet_count": public_metrics.get("tweet_count")
            }
            starkboard_db.update_ecosystem_twitter_social(updated_data)
