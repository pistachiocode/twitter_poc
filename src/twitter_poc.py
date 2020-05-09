import tweepy
import pandas as pd
import numpy as np
import os
import re
import time
import twitter_conf

# -----------
# FUNCTIONS
# -----------


def clean_tweet(text):

    text = re.sub(r'#(\w+)', ' ', text)
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    return(text)


def connect():
    # Twitter authentication

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    return api


def build_query(keyword):

    query = "{} -filter:retweets -result_type:recent -lang:es"

    return query.format(keyword)


def process_tweet(tweet):

    tweet_data = []

    if not "RT" in tweet.full_text:

        tweet_data.append(tweet.created_at)
        tweet_data.append(tweet.id)
        tweet_data.append(tweet.id_str)
        tweet_data.append(tweet.entities['hashtags'])
        tweet_data.append(tweet.metadata['iso_language_code'])

        tweet_data.append("\"" + clean_tweet(tweet.full_text) + "\"")

        tweet_data.append(tweet.retweet_count)
        tweet_data.append(tweet.favorite_count)
        tweet_data.append(tweet.user.id)
        tweet_data.append(tweet.user.id_str)
        tweet_data.append(tweet.user.name)
        tweet_data.append(tweet.user.screen_name)
        tweet_data.append("\"" + clean_tweet(tweet.user.description) + "\"")
        tweet_data.append(tweet.user.followers_count)
        tweet_data.append(tweet.user.friends_count)
        tweet_data.append(tweet.user.statuses_count)
        tweet_data.append(tweet.user.location)

    return tweet_data


# -----------
# MAIN
# -----------

#
# 1. Twitter api connection
#
twitter_api = connect()


for keyword in SEARCH_KEYWORD_LIST:

    print(keyword)

    #
    # 2. Build search query
    #
    query = build_query(keyword)
    print(query)

    #
    # 3. Create output folder
    #

    results_path = DATA_FOLDER + keyword
    if not os.path.isdir(results_path):
        os.mkdir(results_path)

    #
    # 4. Create output file
    #
    results_file_path = results_path + "/tweets.csv"
    results_file = open(results_file_path, "w+")

    #
    # 5. Write columns names
    #
    columns = ['tweet_created_at', 'tweet_id', 'tweet_id_str', 'tweet_hashtags', 'tweet_language', 'tweet_full_text',
               'tweet_retweet_count', 'tweet_favorite_count', 'user_id', 'user_id_str', 'user_name', 'user_screen_name',
               'user_description', 'user_followers_count', 'user_friends_count', 'user_statuses_count', 'user_location']

    results_file.write("\t".join(map(str, columns))+"\n")

    #
    # 6. Get tweets
    #

    # auxiliar variables
    last_date = ""
    attemps = SEARCH_ATTEMPS
    current_max_id = SEARCH_CURRENT_MAX_ID

    global_tweets = 0

    while attemps > 0:

        try:
            print(current_max_id)
            print(last_date)

            #query = query.format(current_max_id)
            interation_tweets = 0

            for tweet in tweepy.Cursor(twitter_api.search, q=query, count=200, max_id=current_max_id, tweet_mode='extended').items(200):

                interation_tweets = interation_tweets + 1
                global_tweets = global_tweets + 1

                # if tweet.id != current_max_id:

                current_max_id = tweet.id
                last_date = tweet.created_at

                tweet_data = process_tweet(tweet)

                results_file.write("\t".join(map(str, tweet_data)) + "\n")

                # save json
                if SEARCH_SAVE_TWEETS:
                    tweet_json_file = open(
                        results_path + "/" + tweet.id_str + ".json", "w")
                    tweet_json_file.write(str(tweet._json))
                    tweet_json_file.close()

            if interation_tweets < 200:
                attemps = attemps - 1

            print("Iteration: {} tweets \n".format(interation_tweets))
            print("Total: {} tweets \n".format(global_tweets))

        except tweepy.TweepError as e:
            print(e)
            time.sleep(60)

    results_file.close()
    print("End")
