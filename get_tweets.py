import tweepy
import configparser
import datetime
import pandas as pd
import pytz
import time 
import csv
import pandas as pd
import random

from config import Config
from db_adapter import DbAdapter
from os.path import abspath, dirname, join
from concurrent.futures import ThreadPoolExecutor
from tweets import Tweets
from time import perf_counter

utc=pytz.UTC

from twarc import Twarc2, expansions
import json
import datetime
import json


# Replace your bearer token below
client = Twarc2(bearer_token="")

tweet_id_cache = Tweets().get_all_tweet_ids(dba)

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

df = pd.read_csv("all_handles.csv")

def parse_tweet(tweet):
            text = tweet['text']
            date_created = tweet['created_at']
            tweet_id = tweet['id']

            d = {
                "username": user,
                "tweet": text,
                "date_created": date_created,
                "tweet_id": tweet_id,
                "followers_count": False

            }

            if d['tweet_id'] not in tweet_id_cache:
                #insert into database 
                f = Tweets(**d)
                f.insert(dba)


for user in df['username']:
     # Specify the start time in UTC for the time period you want Tweets from
    start_time = datetime.datetime(2022, 6, 1, 0, 0, 0, 0, datetime.timezone.utc)

    # Specify the end time in UTC for the time period you want Tweets from
    end_time = datetime.datetime(2023, 1, 31, 0, 0, 0, 0, datetime.timezone.utc)

    # This is where we specify our query as discussed in module 5
    query = "from:" +user 

    # The search_all method call the full-archive search endpoint to get Tweets based on the query, start and end times
    search_results = client.search_all(query=query, start_time=start_time, end_time=end_time, max_results=100)


    # Twarc returns all Tweets for the criteria set above, so we page through the results
    for page in search_results:
        # The Twitter API v2 returns the Tweet information and the user, media etc.  separately
        # so we use expansions.flatten to get all the information in a single JSON
        result = expansions.flatten(page)
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(parse_tweet, result)

