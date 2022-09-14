import time
from dotenv import load_dotenv
load_dotenv()
from starkboard.utils import Requester, StarkboardDatabase
from starkboard.ecosystem.auth import get_twitter_apiv2_auth


def get_application_info(name, api):
    """
    Get the Public Metrics of an Account
    """
    user = api.get_user(username=name, user_fields=["public_metrics", "profile_image_url"])
    try:
        if user.data.profile_image_url:
            profile_picture_url = user.data.profile_image_url.replace("normal", "400x400")
        else:
            profile_picture_url = ""
        return user.data.public_metrics, profile_picture_url
    except Exception as e:
        print(e)
        return None, None


def socials_metrics():
    """
    Fetch Public Metrics and stores it for each Twitter Account in DB
    """
    starkboard_db = StarkboardDatabase()
    list_ecosystem = starkboard_db.get_ecosystem_twitter_handlers()
    twitter_api = get_twitter_apiv2_auth()
    for app in list_ecosystem:
        if app.get("twitter_handler"):
            time.sleep(1)
            public_metrics, profile_picture_url = get_application_info(app.get("twitter_handler"), twitter_api)
            if not public_metrics:
                continue
            print(f'Retrieved Social metrics for {app.get("twitter_handler")}')
            updated_data = {
                "application": app.get("application"),
                "followers_count": public_metrics.get("followers_count"),
                "tweet_count": public_metrics.get("tweet_count"),
                "profile_picture_url": profile_picture_url
            }
            starkboard_db.update_ecosystem_twitter_social(updated_data)
