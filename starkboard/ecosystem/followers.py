import tweepy
from dotenv import load_dotenv
import os
import json
from auth import *

load_dotenv()
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
JSON_FILE_PATH = os.getenv('ECOSYSTEM_JSON_FILE_PATH')


# /!\ WARNING /!\ uses a lot of requests to twitter api
def get_updated_followers():
	client = auth_client(BEARER_TOKEN)

	ecosystem = {}
	with open(JSON_FILE_PATH) as file:
		ecosystem = json.load(file)

	for protocol in ecosystem:
		if 'twitter_id' not in protocol.keys():
			continue
		followers = client.get_users_followers(id=protocol['twitter_id'])
		nb_of_followers = len(followers)
		# still need to make something with the number of followers and test
