import tweepy
from dotenv import load_dotenv
import os
import json
from auth import auth_client

load_dotenv()
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
JSON_FILE_PATH = os.getenv('ECOSYSTEM_JSON_FILE_PATH')


def get_missing_twitter_id_twitter_usernames(ecosystem):
	twitter_usernames = []
	for protocol in ecosystem:
		if 'twitter_id' not in protocol.keys() and protocol['network']['twitter'] != '':
			twitter_username = protocol['network']['twitter'].replace('https://twitter.com/', '')
			twitter_usernames.append(twitter_username)

	return twitter_usernames


def update_missing_twitter_ids():
	ecosystem = {}
	with open(JSON_FILE_PATH) as file:
		ecosystem = json.load(file)

	twitter_usernames = get_missing_twitter_id_twitter_usernames(ecosystem)
	client = auth_client(BEARER_TOKEN)
	i = 1
	while len(twitter_usernames) >= (i-1)*100:
		users = client.get_users(usernames=twitter_usernames[(i-1)*100:i*100])

		for protocol_twitter in users[0]:
			for protocol in ecosystem:
				if protocol_twitter['username'] == protocol['network']['twitter'].replace('https://twitter.com/', ''):
					protocol['twitter_id'] = protocol_twitter['id']
					break

		i = i + 1
	
	with open(JSON_FILE_PATH, 'w') as file:
		json.dump(ecosystem, file, indent=2)
