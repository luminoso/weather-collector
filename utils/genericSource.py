import json
import logging
from abc import abstractmethod
from collections import UserList
from typing import Union, Dict

import requests


class GenericSource(UserList):
    def __init__(self):
        super().__init__()
        # we use the class name as the source name
        self.name = self.__class__.__name__

        # control variable to know differences between API calls refresh
        self._last_data = []

    def fetch_url(self, url: str) -> Union[Dict, None]:
        """
        Fetch a web API
        :param url: to fetch
        :return: resulting json file, if successful
        """

        try:
            req = requests.get(url)
            req.raise_for_status()
            res = req.json()
        except (requests.HTTPError, json.JSONDecodeError) as e:
            logging.warning(f'{self.__class__.__name__} failed to retrieve/parse {url}')
            # logging.debug(e)
            return

        # safe-check for empty response from server
        if not res:
            logging.warning(f"{self.__class__.__name__} empty response from {url}")
            return

        return res

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.data}'

    def calculate_incremental(self):
        """
        Tries to strip already collected data from last API refresh calls
        :return: a list with the incremental difference only
        """
        tmp = [x for x in self.data if x not in self._last_data]

        # consecutive refreshes are compared with latest block with atual data, not with latest empty diff
        if self.data:
            self._last_data = self.data

        self.data = tmp

        logging.debug(f'Sending incremental changes from {len(self._last_data)} messages to {len(self.data)}')

    @staticmethod
    def append_ipma_metadata(orig: dict, dest: dict):
        """
        Appends outside metadata to the inner 'data' field

        :param orig: api call metadata
        :param dest: dictionary to append to
        """
        for key in [key for key in orig.keys() if key != 'data']:
            dest[key] = orig[key]

    @abstractmethod
    def refresh_source(self):
        """
        This method should be implemented with the nuances of each API specific call
        """
        pass
