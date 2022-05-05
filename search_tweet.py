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

import params as PARAMS

warnings.filterwarnings("ignore")

AUTH = TwitterOAuth.read_file(PARAMS.TWITTER_CREDENTIALS)

API =  TwitterAPI(
            AUTH.consumer_key,
            AUTH.consumer_secret,
            AUTH.access_token_key,
            AUTH.access_token_secret,
            auth_type='oAuth2',
            api_version='2'
        )

def parse_tweets(results):
    tweets = pd.DataFrame()

    for item in results:
        sentiment_score = s.polarity_scores(item['text'])['compound']

        if sentiment_score > 0:
            sentiment = 'positive'
        elif sentiment_score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

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
            'sentiment_score': sentiment_score if sentiment_score <= 1.0 and sentiment_score >= -1.0 else 0.0,
            'sentiment':       sentiment
        }

        if 'location' in item['author_id_hydrate'].keys():
            tweet['location'] = item['author_id_hydrate']['location']

        if 'referenced_tweets' in item.keys():
            tweet['origin_tweet_id'] = item['referenced_tweets'][0]['id']
            tweet['type'] = item['referenced_tweets'][0]['type']

        tweets = tweets.append(tweet, ignore_index=True)
    
    return {'tweets': tweets}


# query = "\"Uber\" lang:pt"
since_id = None

def search(query):
    try:
        params = {
            'query': {query}, 
            'expansions': PARAMS.EXPANSIONS,
            'tweet.fields': PARAMS.TWEET_FIELDS,
            'user.fields': PARAMS.USER_FIELDS,
            'max_results': 100
        }
        
        if since_id is not None:
            params['since_id'] = since_id

        results = API.request('tweets/search/recent', 
            params,
            hydrate_type = HydrateType.APPEND
        )

        dfs_tweets = parse_tweets(results)
        
        dfs_tweets['tweets'].to_csv('tweets.csv', index = False, decimal='.')

    except TwitterRequestError as e:
        print(e.status_code)
        for msg in iter(e):
            print('Mistake', msg)

    except TwitterConnectionError as e:
        print('Connection Error', e)

    except Exception as e:
        print('Exception', e)
