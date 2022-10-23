from ast import keyword
import json

import os
import re
import pandas as pd
import time
import tweepy
from tweepy import SearchResults
from config.config import Config

from twitter_engine.keywords import KeywordManager


TWEET_FIELDS = [
    "tweet_created_at",
    "tweet_id",
    "tweet_id_str",
    "tweet_hashtags",
    "tweet_language",
    "tweet_full_text",
    "tweet_retweet_count",
    "tweet_favorite_count",
    "tweet_in_reply_to_status_str",
    "user_id",
    "user_id_str",
    "user_name",
    "user_screen_name",
    "user_description",
    "user_followers_count",
    "user_friends_count",
    "user_statuses_count",
    "user_location",
    "user_verified",
]


class TwitterKeys:

    with open(Config.API_CONFIG_FILE) as fconfig:
        config = json.load(fconfig)

    CONSUMER_KEY = config["TWITTER_CONSUMER_KEY"]
    CONSUMER_SECRET = config["TWITTER_CONSUMER_SECRET"]
    ACCESS_TOKEN = config["TWITTER_ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = config["TWITTER_ACCESS_TOKEN_SECRET"]


class TextUtils:
    @staticmethod
    def clean_tweet(text: str) -> str:
        """
        This method returns a cleaned text removing non-letter characters, breaklines
        and tabs.

        :param text: input string
        :type text: str
        :return: cleaned text
        :rtype: str
        """

        text = re.sub(r"#(\w+)", " ", text)
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")

        return text


class TwitterSearchOptions:
    def __init__(self, keywords: KeywordManager):

        self.max_id = -1
        self.attemps = 3
        self.save_tweets = True

        self.keywords = keywords
        self.twitter_keys = TwitterKeys()

    def connect(self):
        """
        Twitter connection
        """

        auth = tweepy.OAuthHandler(
            self.twitter_keys.CONSUMER_KEY, self.twitter_keys.CONSUMER_SECRET
        )
        auth.set_access_token(
            self.twitter_keys.ACCESS_TOKEN, self.twitter_keys.ACCESS_TOKEN_SECRET
        )

        self.api = tweepy.API(
            auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
        )

    @staticmethod
    def build_query(keyword) -> str:
        """
        Creation of a twitter query from an input keyword

        :param keyword: Input keyword
        :type keyword: str
        :return: Twitter API query
        :rtype: str
        """

        query = "{} -filter:retweets -result_type:recent"

        return query.format(keyword)

    @staticmethod
    def process_tweet(tweet: SearchResults) -> list:
        """
        This method creates a list from a Tweet object that contains the some
        relevant information.

        :param tweet: Tweet object
        :param tweet: Tweet
        :return: output list with a subset of a Tweet information
        :rtype: list
        """

        tweet_data = []

        if not "RT" in tweet.full_text:
            tweet_data.append(tweet.created_at)
            tweet_data.append(tweet.id)
            tweet_data.append(tweet.id_str)
            tweet_data.append(tweet.entities["hashtags"])
            tweet_data.append(tweet.metadata["iso_language_code"])
            tweet_data.append('"' + TextUtils.clean_tweet(tweet.full_text) + '"')
            tweet_data.append(tweet.retweet_count)
            tweet_data.append(tweet.favorite_count)
            tweet_data.append(tweet.in_reply_to_status_id_str)
            tweet_data.append(tweet.user.id)
            tweet_data.append(tweet.user.id_str)
            tweet_data.append(tweet.user.name)
            tweet_data.append(tweet.user.screen_name)
            tweet_data.append('"' + TextUtils.clean_tweet(tweet.user.description) + '"')
            tweet_data.append(tweet.user.followers_count)
            tweet_data.append(tweet.user.friends_count)
            tweet_data.append(tweet.user.statuses_count)
            tweet_data.append(tweet.user.location)
            tweet_data.append(tweet.user.verified)

        return tweet_data

    def search_tweet_replies(self, name: str, tweet_id: str = None):
        """
        Get replies to tweet
        """
        replies = []
        for tweet in tweepy.Cursor(
            self.api.search,
            q="to:" + name,
            result_type="recent",
            timeout=999999,
            tweet_mode="extended",
        ).items(1000):
            if tweet_id is not None:
                if (
                    not hasattr(tweet, "in_reply_to_status_id_str")
                    and tweet.in_reply_to_status_id_str != tweet_id
                ):
                    continue

            tweet_data = self.process_tweet(tweet)
            replies.append(tweet_data)

        df = pd.DataFrame(replies)
        df.columns = TWEET_FIELDS
        return df

    def search_tweets_by_keyword(self):
        """

        :return:
        """

        for k in self.keywords:

            keyword = k["keyword"]
            keyword_max_id = k["max_id"]

            # reset attemps
            self.attemps = 3

            print(f"Extracting tweets of keyword: {keyword}")
            query = self.build_query(keyword)

            # Create output query
            results_path = os.path.join(Config.DATA_FOLDER, keyword.replace("#", ""))
            if not os.path.isdir(results_path):
                os.makedirs(results_path, exist_ok=True)

            results_file_path = results_path + "/tweets.csv"
            results_file = open(results_file_path, "w+")

            results_file.write("\t".join(map(str, TWEET_FIELDS)) + "\n")

            # auxiliar variables
            last_date = ""
            current_max_id = keyword_max_id

            global_tweets = 0

            while self.attemps > 0:

                print("CURRENT_MAX_ID: {}".format(current_max_id))
                print(last_date)

                interation_tweets = 0

                try:

                    for tweet in tweepy.Cursor(
                        self.api.search,
                        q=query,
                        max_id=current_max_id,
                        tweet_mode="extended",
                    ).items(200):
                        interation_tweets = interation_tweets + 1
                        global_tweets = global_tweets + 1

                        # if tweet.id != current_max_id:

                        current_max_id = tweet.id
                        last_date = tweet.created_at

                        tweet_data = self.process_tweet(tweet)

                        results_file.write("\t".join(map(str, tweet_data)) + "\n")

                        # save json
                        if self.save_tweets:
                            tweet_json_file = open(
                                results_path + "/" + tweet.id_str + ".json", "w"
                            )
                            tweet_json_file.write(str(tweet._json))
                            tweet_json_file.close()

                    if interation_tweets < 200:
                        self.attemps = self.attemps - 1

                    print("Iteration: {} tweets \n".format(interation_tweets))
                    print("Total: {} tweets \n".format(global_tweets))

                except tweepy.TweepError as e:
                    print(e)
                    time.sleep(60)

            self.keywords.update_keyword(keyword, current_max_id)
            results_file.close()

        self.keywords.save_keywords()
