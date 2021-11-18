#!python

import logging
import pandas as pd
import requests
import os
import json
import uuid
import tqdm
import time
import validators

from tqdm import tqdm
from pandas import json_normalize
from datetime import date
from .TwitterFullArchive import GetStatsFromTweets, GetTweetsFromUser, GetStatsFromUsers, GetInteractionsAssociatedToLink
from .AuxTweetPle import df_tweets_stats, df_users_stats, roundup, agg_stats, twitter_df

class TweepleStreamer:

    """Retrieves timelines from a list of tweeplers (handles)"""

    def __init__(self,
                 ids,
                 bearer_token,
                 save = False,
                 file_name = 'tweeplers',
                 path_save:str or None = '.'):
                 self.bearer_token = bearer_token
                 self.ids = ids
                 self.file_name = file_name
                 self.path_save = path_save
                 self.save = save

    def main(self):
        logging.basicConfig(filename=self.file_name + '.log', level=logging.INFO)
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

    """Retrieves tweets from a list of tweets, handles or links"""

    def __init__(self,
                 data,
                 bearer_token,
                 file_name = 'tweets',
                 path_save:str or None = './',
                 column_link = 'links.streamed',
                 start_time = "2006-03-26T00:00:00Z",
                 end_time = str(date.today())+'T00:00:00Z'):
                 self.bearer_token = bearer_token
                 self.column_link = column_link
                 self.data = data
                 self.file_name = file_name
                 self.path_save = path_save
                 self.start_time = start_time
                 self.end_time = end_time

    def streamer_handles(self):

        """Retrieves tweets from a list of twitter handles"""

        logging.basicConfig(filename='streamer_handles.log', level=logging.INFO)
        start_time = time.time()
        for handle in tqdm(self.data):
            try:
                stat = GetTweetsFromUser(
                handle,
                self.bearer_token,
                self.start_time,
                self.end_time
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

    def streamer_links(self):
        df_stats = twitter_df(self.column_link)
        for url in tqdm(self.data):
            time.sleep(1)
            stat = GetInteractionsAssociatedToLink(
            url,
            self.bearer_token,
            self.column_link,
            self.start_time,
            self.end_time
            )
            stats = stat.main()
            df_stats= df_stats.append(stats, ignore_index=True)
        df_stats.to_parquet(self.path_save + self.file_name + '.parquet')
        stats = agg_stats(df_stats, self.column_link)
        stats.to_parquet(self.path_save +'agg_stats.parquet')

    def main(self):
        """
        Run tweets wrapper
        """
        # validate type of input
        input = self.data[0]

        if input.isnumeric()==True:
            #list of tweet ids
            self.streamer_tweetids()

        elif validators.url(input) is True:
            #list of urls
            self.streamer_links()

        else:
            #list of handles
            self.streamer_handles()
