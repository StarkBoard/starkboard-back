import tweepy

def auth_client(bearer_token):
		client = tweepy.Client(bearer_token)

		return client 
