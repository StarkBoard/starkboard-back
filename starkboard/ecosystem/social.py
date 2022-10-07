import time
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from starkboard.utils import Requester, StarkboardDatabase
from starkboard.ecosystem.auth import get_twitter_apiv2_auth, get_starknet_ecosystem_db_token
from starkboard.ecosystem.fetch_application import get_starknet_db_ecosystem, normalize_list_applications

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


def socials_offchain_metrics():
    """
    Fetch Public Metrics and stores it for each Twitter Account in DB
    """
    list_ecosystem, count_ecosystem = get_starknet_db_ecosystem()
    list_ecosystem = normalize_list_applications(list_ecosystem)
    twitter_api = get_twitter_apiv2_auth()
    starknet_db = Requester(os.environ.get('STARKNET_ECOSYSTEM_DB_URL'))
    bearer = get_starknet_ecosystem_db_token()
    headers = {'Content-Type': 'application/json'}
    headers['Authorization'] = f'Bearer {bearer}'
    for app in list_ecosystem:
        if app.get("twitter"):
            twitter_handle = app.get("twitter").split('/')[-1]
            time.sleep(1)
            public_metrics, profile_picture_url = get_application_info(twitter_handle, twitter_api)
            if not public_metrics:
                continue
            data = {
                "twitterFollower": public_metrics.get("followers_count"),
                "twitterCount": public_metrics.get("tweet_count"),
                "tweetWithStarknet": 0,
                "socialActivity": 0,
                "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + datetime.now().strftime('.%f')[:4] + 'Z'
            }
            starknet_db.post(url=f"projects/{app.get('id')}/social-metrics", params=data, headers=headers)
            print(f'Retrieved Social metrics for {twitter_handle} ({app.get("id")})')
