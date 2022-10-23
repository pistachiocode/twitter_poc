import os
from pathlib import Path


class Config:

    ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "config"

    #
    # Keywords search json
    #
    SEARCH_FILE = os.path.join(ROOT_DIR, "search.json")

    #
    # Folder used to store extracted tweets
    #
    DATA_FOLDER = os.path.join(ROOT_DIR, "data")

    #
    # Analysis results folders
    #
    RESULTS_FOLDER = os.path.join(ROOT_DIR, "results")

    #
    # Logs folder
    #

    LOGS_FOLDER = os.path.join(ROOT_DIR, "logs")

    #
    # Config file
    #
    API_CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")

    #
    # Formats
    #
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT
