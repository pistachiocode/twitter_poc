import json
from config.config import Config
from twitter_engine.keywords import KeywordManager
from twitter_engine.twitter_engine import TwitterSearchOptions

INIT_MAX_ID = -1
INIT_SINDE_ID = 0
COUNT = 200
LANG = "es"


if __name__ == "__main__":

    keywords = KeywordManager()
    keywords.load_keywords()

    twitter_search = TwitterSearchOptions(keywords)
    twitter_search.connect()
    twitter_search.search_tweets_by_keyword()

    # How many tweets? When it shoud stop?
    # of n of tweets or time of execution

    # Explore functionalities
    # - get TT hashtags
    # - get TT hashtag topic
    # - get tweets of an user
    # - get all tweet answers
