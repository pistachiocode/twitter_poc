import json
import pandas as pd

from config.config import Config

INIT_MAX_ID = -1
INIT_SINDE_ID = 0
COUNT = 200
LANG = "es"


class KeywordManager:
    def __init__(self):
        self.keywords = {}

    def load_keywords(self):
        """
        Load keywords state from .json file
        """
        with open(Config.SEARCH_FILE, "r") as f:
            self.keywords = json.load(f)

    def add_keyword(self, keyword: str):
        """
        Add a new keyword with default configuration
        """
        self.keywords[keyword] = {
            "max_id": INIT_MAX_ID,
            "since_id": INIT_SINDE_ID,
            "lang": LANG,
            "count": COUNT,
        }

    def update_keyword(self, keyword: str, max_id: int, since_id: int):
        """
        Update keyword state
        """
        self.keywords[keyword]["max_id"] = max_id
        self.keywords[keyword]["since_id"] = since_id

    def save_keywords(self):
        """
        Save currenct keywords state
        """
        with open(Config.SEARCH_FILE, "w", encoding="utf-8") as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=4)

    def __iter__(self):
        return KeywordIterator(self)


class KeywordIterator:
    def __init__(self, keywords: KeywordManager):
        self._keywords = keywords.keywords
        self._class_size = len(self._keywords.keys())
        self._current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < self._class_size:
            keys = list(self._keywords.keys())
            member_key = keys[self._current_index]
            member = self._keywords[member_key]
            self._current_index += 1
            return member

        raise StopIteration
