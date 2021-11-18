#!python

import logging
import pandas as pd
import requests
import os
import json
import uuid
import tqdm
import time

from tqdm import tqdm
from pandas import json_normalize
from datetime import date
from .TwitterFullArchive import GetStatsFromTweets, GetTweetsFromUser, GetStatsFromUsers
from .AuxTweetPle import df_tweets_stats, df_users_stats, roundup

class TweepleStreamer:

    """Retrieves stats from a list of twitter handles"""

    def __init__(self,
                 ids,
                 bearer_token,
                 save = False,
                 file_name:str or None = None,
                 path_save:str or None = '.'):
                 self.bearer_token = bearer_token
                 self.ids = ids
                 self.file_name = file_name
                 self.path_save = path_save
                 self.save = save

    def main(self):
        logging.basicConfig(filename='users_handles' + str(date.today()) + '.log', level=logging.INFO)
        start_time = time.time()
        df_stats = df_users_stats()
        end = roundup(len(self.ids))+100
        bounds = list(range(0, end, 100))

        for prev, curr in tqdm(zip(bounds, bounds[1:])):

            stat = GetStatsFromUsers(
            self.ids[prev:curr],
            self.bearer_token
            )
            df_stats = df_stats.append(
            stat.main(),
            ignore_index = True
          )

        if self.save:
            df_stats.to_parquet(f'{self.path_save}{self.file_name}.parquet')

        logging.info("Done in {} seconds".format(str(time.time() - start_time)))

        return(df_stats)

class TweetStreamer:
    def __init__(self,
                 data,
                 bearer_token,
                 handles=True,
                 file_name:str or None = None,
                 path_save:str or None = './'):
                 self.bearer_token = bearer_token
                 self.data = data
                 self.handles = handles
                 self.file_name = file_name
                 self.path_save = path_save

    def streamer_handles(self):

        """Retrieves tweets from a list of twitter handles"""

        logging.basicConfig(filename='streamer_handles.log', level=logging.INFO)
        start_time = time.time()
        for handle in tqdm(self.data):
            try:
                stat = GetTweetsFromUser(
                handle,
                self.bearer_token
                )
                stats = stat.main()
                stats.to_parquet(self.path_save + handle +'.parquet')
            except:
                logging.exception("Failed to retrieve tweets from {}".format(handle))
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))

    def streamer_tweetids(self):

        """Retrieves stats from a list of tweets"""

        logging.basicConfig(filename='streamer_tweetids.log', level=logging.INFO)
        start_time = time.time()
        df_stats = df_tweets_stats()
        end = roundup(len(self.data))+100
        bounds = list(range(0, end, 100))
        for prev, curr in tqdm(zip(bounds, bounds[1:])):
            stat = GetStatsFromTweets(
            self.data[prev:curr],
            self.bearer_token
            )
            df_stats = df_stats.append(
            stat.main(),
            ignore_index = True
          )
        df_stats.to_parquet(self.path_save + self.file_name +'.parquet')
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))
        return(df_stats)

    def main(self):
        if self.handles:
            self.streamer_handles()
        else:
            self.streamer_tweetids()
