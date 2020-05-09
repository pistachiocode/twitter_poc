import json

# -----------
# CONSTANTS
# -----------

#
# Folder used to store extracted tweets
#
DATA_FOLDER = "../data/"

#
# Analysis results folders
#
RESULTS_FOLDER = "../results/"

#
# Logs folder
#

LOGS_FOLDER = "../logs/"

#
# Formats
#
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = DATE_FORMAT+' '+TIME_FORMAT

#
# Search options
#
SEARCH_CURRENT_MAX_ID = -1
SEARCH_ATTEMPS = 3
SEARCH_SAVE_TWEETS = True
SEARCH_KEYWORD_LIST = ["VOX"]
SEARCH_KEYWORD = "#SesiondeInvestidura"


with open("../config.json") as fconfig:
    config = json.load(fconfig)

CONSUMER_KEY = config["CONSUMER_KEY"]
CONSUMER_SECRET = config["CONSUMER_SECRET"]
ACCESS_TOKEN = config["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = config["ACCESS_TOKEN_SECRET"]

DATA_FOLDER = "../data/"
