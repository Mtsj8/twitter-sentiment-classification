import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

import pytest
import search_tweet
import params as PARAMS
from TwitterAPI import TwitterOAuth
from TwitterAPI import HydrateType
import json


AUTH = TwitterOAuth.read_file(PARAMS.TWITTER_CREDENTIALS)


def test_api_connection():
    api = search_tweet.twitter_api_connection(AUTH)
    
    assert api is not None


def call_twitter_api():
    query = "\"Uber\" lang:pt"
    params = {
            'query': {query}, 
            'expansions': PARAMS.EXPANSIONS,
            'tweet.fields': PARAMS.TWEET_FIELDS,
            'user.fields': PARAMS.USER_FIELDS,
            'max_results': 10
        }
    
    api = search_tweet.twitter_api_connection(AUTH)
    results = api.request(
            'tweets/search/recent', 
            params,
            hydrate_type = HydrateType.APPEND)

    return results


def test_api_call():
    results = call_twitter_api()
    
    assert len(results.json()['data']) is 10


def test_parse_information():
    tweets = search_tweet.parse_tweets(PARAMS.MOCK_RESULTS['data'])['tweets']

    count_sentiment_score_null = tweets['sentiment_score'].isnull().sum()

    assert count_sentiment_score_null == 0


def test_create_csv():
    tweets = search_tweet.parse_tweets(PARAMS.MOCK_RESULTS['data'])['tweets']
    filename = 'tweets_Uber'
    search_tweet.create_csv(tweets, filename)

    assert os.path.exists('tweets/%s.csv' % (filename))

def test_full_search():
    query = "\"Uber\" lang:pt"
    filename = "tweets_Uber"

    df = search_tweet.search(query, filename)

    assert len(df) != 0
