#!/usr/bin/env python3
# encoding: utf-8
# ============================================================================

import logging
import pandas as pd
import tqdm
import time
import validators

from tqdm import tqdm
from datetime import date
from .TwitterFullArchive import TwitterObject, GetStatsFromTweets, GetTweetsFromUser, GetStatsFromUsers, GetInteractionsAssociatedToLink, GetFollowers
from .AuxTweetPle import df_tweets_stats, df_users_stats, roundup, aggregate_twitter_metrics, twitter_df


class TweepleStreamer:

    """Users and Followers Lookup

    Attributes
    ----------
    ids : str
        List of ids we want to retrieve information from
    path_save:str
        Path to save data collected
    save : Boolean
        To save information
        Defaults to False
    bearer_token : str
        Bearer token

    Methods
    -------
    user_lookup()
        Users lookup
    followers_lookup()
        Followers lookup
    """

    def __init__(self, ids, bearer_token, save = False, path_save = './'):
        self.bearer_token = bearer_token
        self.ids = ids
        self.file_name = 'tweeplers'
        self.path_save = path_save
        self.save = save


    def user_lookup(self):
        """Retrieves tweetples' information
        ...

        """
        logging.basicConfig(filename=f'{self.file_name}_lookup.log', level=logging.INFO)
        start_time = time.time()

        df_stats = df_users_stats()

        end = roundup(len(self.ids)) + 100
        bounds = list(range(0, end, 100))
        for prev, curr in tqdm(zip(bounds, bounds[1:])):
            stat = GetStatsFromUsers(self.ids[prev:curr], self.bearer_token)
            df_stats = df_stats.append(
                stat.main(),
                ignore_index = True
            )
        if self.save:
            df_stats.to_parquet(f'{self.path_save}{self.file_name}.parquet')
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))


        return df_stats


    def followers_lookup(self):
        """Retrieves followers' information
        ...

        """
        logging.basicConfig(filename=f'{self.file_name}_followers.log', level=logging.INFO)
        start_time = time.time()
        not_scraped = []

        for id_user in tqdm(self.ids):

            try:

                df = GetFollowers(id_user, self.bearer_token).main()
                df.to_parquet(f"{self.path_save}{id_user}.parquet")

            except:
                not_scraped.append(id_user)
                time.sleep(60)

        logging.info(f"Ids not scraped: {not_scraped}")
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))


class TweetStreamer:

    """Retrieves tweets from a list of tweets, handles or links
    ...

    Attributes
    ----------
    data : str
        List of tweets, handles or links
    path_save:str or None = '.'):
        Path to save data collected
    bearer_token : str
        Bearer token
    start_time : timestamp
        Start date to retrieve information from
        Defaults  to `2006-03-26T00:00:00Z`
    end_time : timestamp
        End date to retrieve information from
        Defaults to `today`

    Methods
    -------
    streamer_handles()
        Tweets from a list of Twitter handles
    streamer_tweetids()
        Stats from a list of tweets
    streamer_links()
        Stats from a list of links
    main()
        Execute the streamer
    """


    def __init__(self, data, bearer_token, path_save:str or None = './', start_time = "2006-03-26T00:00:00Z", end_time = str(date.today())+'T00:00:00Z'):
        self.bearer_token = bearer_token
        self.column_link = 'links.streamed'
        self.data = data
        self.file_name = 'tweets'
        self.path_save = path_save
        self.start_time = start_time
        self.end_time = end_time


    def streamer_handles(self):

        """Retrieves tweets from a list of Twitter handles
        ...

        """
        logging.basicConfig(filename='streamer_handles.log', level=logging.INFO)
        start_time = time.time()
        search_url = "https://api.twitter.com/2/tweets/search/all"
        for handle in tqdm(self.data):
            try:
                stat = GetTweetsFromUser(handle, self.bearer_token, self.start_time, self.end_time, search_url).main()
                stat.to_parquet(self.path_save + handle +'.parquet')
            except:
                logging.exception("Failed to retrieve tweets from {}".format(handle))
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))


    def streamer_tweetids(self):

        """Retrieves stats from a list of tweets
        ...

        """
        logging.basicConfig(filename='streamer_tweetids.log', level=logging.INFO)
        start_time = time.time()
        df_stats = df_tweets_stats()
        end = roundup(len(self.data))+100
        bounds = list(range(0, end, 100))
        for prev, curr in tqdm(zip(bounds, bounds[1:])):
            stat = GetStatsFromTweets(self.data[prev:curr],self.bearer_token)
            df_stats = df_stats.append(
                stat.main(),
                ignore_index = True
            )
        df_stats.to_parquet(f'{self.path_save}{self.file_name}.parquet')
        logging.info("Done in {} seconds".format(str(time.time() - start_time)))


        return df_stats


    def streamer_links(self):

        """Retrieves tweets containing links
        ...

        """

        search_url = "https://api.twitter.com/2/tweets/search/all"
        df_stats = twitter_df(self.column_link)
        for url in tqdm(self.data):
            time.sleep(1)
            stat = GetInteractionsAssociatedToLink(
                url, self.bearer_token, self.column_link, self.start_time, self.end_time, search_url
                )
            df_stats= df_stats.append(stat.main(), ignore_index=True)
        df_stats.to_parquet(f'{self.path_save}{self.file_name}.parquet')
        stats = aggregate_twitter_metrics(df_stats, self.column_link)
        stats.to_parquet(f'{self.path_save}agg_stats.parquet')


    def main(self):
        """Run tweets wrapper

        """
        # validate type of input
        input_str = self.data[0]

        if input_str.isnumeric()==True:
            #list of tweet ids
            self.streamer_tweetids()

        elif validators.url(input_str) is True:
            #list of urls
            self.streamer_links()

        else:
            #list of handles
            self.streamer_handles()
