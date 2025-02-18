import tweepy
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from textblob import TextBlob
import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# need to subscribe to higher tier of the API

class TwitterSentimentAnalyzer:

    def __init__(self, api_key, api_secret, access_token, access_token_secret, bearer_token):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.Client(bearer_token=bearer_token, 
                                access_token=access_token, 
                                access_token_secret=access_token_secret, 
                                wait_on_rate_limit=True
                            )

    def fetch_tweets(self, query, start_date, end_date, count=10):
        # Fetch tweets based on query and date range
        tweets = tweepy.Paginator(self.api.search_all_tweets,
                                query=query,
                                start_time=start_date, 
                                end_time=end_date,
                                max_result=10
                                ).flatten(limit=count)
        tweet_data = [(tweet.text, tweet.public_metrics['like_count']) for tweet in tweets]
        return pd.DataFrame(tweet_data, columns=['text', 'likes'])

    def analyze_sentiment(self, df):
        # Perform sentiment analysis on tweets
        df['sentiment'] = df['text'].apply(lambda text: TextBlob(text).sentiment.polarity)
        return df

    def get_average_sentiment(self, df):
        return df['sentiment'].mean()

    def run_analysis(self, query, hours=24, count=100):
        # Define date range for the last 24 hours
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d')

        # Fetch and analyze tweets
        df = self.fetch_tweets(query, start_date, end_date, count)
        df = self.analyze_sentiment(df)
        average_sentiment = self.get_average_sentiment(df)

        return average_sentiment
    
load_dotenv('PATH_TO_.ENV_FILE')
api_key = os.getenv('TWITTER_API_KEY')
api_secret_key = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN_KEY')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

analyzer = TwitterSentimentAnalyzer(api_key, api_secret_key, access_token, access_token_secret, bearer_token)
average_sentiment = analyzer.run_analysis('$BTC')
print(f'Average Sentiment Score: {average_sentiment}')
