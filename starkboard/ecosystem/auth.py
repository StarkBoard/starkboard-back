import os
import tweepy
from dotenv import load_dotenv
load_dotenv()

#
# Twitter Off Chain
#

def get_twitter_apiv2_auth():
	"""
	# Authenticate to Twitter V2
	"""
	try:
		bearer_token = os.environ.get('TWITTER_BEARER')
		api = tweepy.Client(bearer_token)
		print('Twitter Successful Authentication')
		return api
	except Exception as e:
		print('Twitter Failed authentication')
		return None

def get_twitter_apiv1_auth():
	"""
	# Authenticate to Twitter V1
	"""
	try:
		consumer_key = os.environ.get('TWITTER_KEY')
		consumer_secret = os.environ.get('TWITTER_SECRET')
		access_token = os.environ.get('TWITTER_ACCESS_KEY')
		access_token_secret = os.environ.get('TWITTER_ACCESS_SECRET')
		auth = tweepy.OAuth1UserHandler(
			consumer_key, consumer_secret, access_token, access_token_secret
		)
		api = tweepy.API(auth)
		return api
	except Exception as e:
		print('Twitter Failed authentication')
		return None
