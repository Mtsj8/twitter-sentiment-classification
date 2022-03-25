from LeIA.leia import SentimentIntensityAnalyzer

s = SentimentIntensityAnalyzer()

from TwitterAPI import TwitterOAuth
from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterConnectionError
from TwitterAPI import TwitterRequestError
from TwitterAPI import HydrateType

import pandas as pd

from os import path
import warnings

warnings.filterwarnings("ignore")

EXPANSIONS = ("author_id,referenced_tweets.id,"
              "referenced_tweets.id.author_id,"
              "in_reply_to_user_id,attachments.media_keys")

TWEET_FIELDS = 'created_at,author_id,public_metrics'

USER_FIELDS = 'location,verified,public_metrics'

CURRENT_PATH = path.dirname(__file__)  
TWITTER_CREDENTIALS = path.join(CURRENT_PATH, './credentials.txt')

AUTH = TwitterOAuth.read_file(TWITTER_CREDENTIALS)

API =  TwitterAPI(
            AUTH.consumer_key,
            AUTH.consumer_secret,
            AUTH.access_token_key,
            AUTH.access_token_secret,
            auth_type='oAuth2',
            api_version='2'
        )

def parse_origin_tweet(origin_tweet_item, origin_tweets = pd.DataFrame()):
    sentiment_score = s.polarity_scores(origin_tweet_item['id_hydrate']['text'])['compound']

    origin_tweet = {
        'id':              origin_tweet_item['id'],
        'author_id':       origin_tweet_item['id_hydrate']['author_id'],
        'content':         origin_tweet_item['id_hydrate']['text'],
        'created_at':      origin_tweet_item['id_hydrate']['created_at'],
        'replies':         origin_tweet_item['id_hydrate']['public_metrics']['reply_count'],
        'likes':           origin_tweet_item['id_hydrate']['public_metrics']['like_count'],
        'quotes':          origin_tweet_item['id_hydrate']['public_metrics']['quote_count'],
        'sentiment_score': sentiment_score if sentiment_score <= 1.0 and sentiment_score >= -1.0 else 0.0
    }

    origin_tweets = origin_tweets.append(origin_tweet, ignore_index=True)

    return origin_tweets

def parse_tweets(results):
    tweets = pd.DataFrame()
    origin_tweets = pd.DataFrame()

    for item in results:
        sentiment_score = s.polarity_scores(item['text'])['compound']
        tweet = {
            'id':              item['id'],
            'author_id':       item['author_id'],
            'content':         item['text'],
            'created_at':      item['created_at'],
            'verified':        item['author_id_hydrate']['verified'],
            'retweets':        item['public_metrics']['retweet_count'],
            'replies':         item['public_metrics']['reply_count'],
            'likes':           item['public_metrics']['like_count'],
            'quotes':          item['public_metrics']['quote_count'],
            'followers_count': item['author_id_hydrate']['public_metrics']['followers_count'],
            'sentiment_score': sentiment_score if sentiment_score <= 1.0 and sentiment_score >= -1.0 else 0.0
        }

        if 'location' in item['author_id_hydrate'].keys():
            tweet['location'] = item['author_id_hydrate']['location']

        if 'referenced_tweets' in item.keys():
            tweet['origin_tweet_id'] = item['referenced_tweets'][0]['id']
            tweet['type'] = item['referenced_tweets'][0]['type']

            if 'id_hydrate' in item['referenced_tweets'][0].keys():
                origin_tweets = parse_origin_tweet(item['referenced_tweets'][0], origin_tweets)

        tweets = tweets.append(tweet, ignore_index=True)
    
    return {'tweets': tweets, 'origin_tweets': origin_tweets}


query = "\"Uber\" lang:pt"
since_id = None

try:
    params = {
        'query': {query}, 
        'expansions': EXPANSIONS,
        'tweet.fields': TWEET_FIELDS,
        'user.fields': USER_FIELDS,
        'max_results': 100
    }
    
    if since_id is not None:
        params['since_id'] = since_id

    results = API.request('tweets/search/recent', 
        params,
        hydrate_type = HydrateType.APPEND
    )

    dfs_tweets = parse_tweets(results)
    
    dfs_tweets['tweets'].to_csv('tweets.csv', index = False)
    dfs_tweets['origin_tweets'].to_csv('origin_tweets.csv', index = False)

except TwitterRequestError as e:
    print(e.status_code)
    for msg in iter(e):
        print('Mistake', msg)

except TwitterConnectionError as e:
    print('Connection Error', e)

except Exception as e:
    print('Exception', e)