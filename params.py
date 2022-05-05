from os import path

EXPANSIONS = ("author_id,referenced_tweets.id,"
              "referenced_tweets.id.author_id,"
              "in_reply_to_user_id,attachments.media_keys")


TWEET_FIELDS = 'created_at,author_id,public_metrics'

USER_FIELDS = 'location,verified,public_metrics'

CURRENT_PATH = path.dirname(__file__)  
TWITTER_CREDENTIALS = path.join(CURRENT_PATH, './credentials.txt')