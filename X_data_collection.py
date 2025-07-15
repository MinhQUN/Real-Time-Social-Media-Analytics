import tweepy
import pandas as pd
import json
from datetime import datetime

# Twitter API credentials
consumer_key = 'V8IXh2jTrolGv295W14JHIgP7'
consumer_secret = 'wHOcbthoEBgRauImFNzaBmcQixDnMnPIHjP9PbwcQB1srAaomA'
access_token = '1812368902867046400-xnn3nwl5Royb1yDQQDMwJt2vWkWcP9'
access_token_secret = 'ImIUOgy7TXZbD5p5uSlOqcFEjD3ZCRM42Hlg2FijKK5kE'

# Authenticate with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def collect_tweets(hashtag, count=100):
    tweets_data = []
    
    tweets = tweepy.Cursor(api.search_tweets, 
                          q=hashtag, 
                          tweet_mode='extended',
                          lang='en').items(count)
    
    for tweet in tweets:
        tweets_data.append({
            'tweet_id': tweet.id,
            'text': tweet.full_text,
            'user': tweet.user.screen_name,
            'followers': tweet.user.followers_count,
            'retweets': tweet.retweet_count,
            'likes': tweet.favorite_count,
            'created_at': tweet.created_at,
            'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])]
        })
    
    return pd.DataFrame(tweets_data)

# Collect data
df_tweets = collect_tweets('#DataScience', 200)
df_tweets.to_csv('twitter_data.csv', index=False)
