# ============================================================================

# Classes to retrieve data from Twitters "Full-Archive Search" Endpoint

# ============================================================================

import requests
import os
import json
import uuid
import tqdm
import pandas as pd
import time

from tqdm import tqdm
from pandas import json_normalize
from datetime import date


class GetInteractionsAssociatedToLink:

    """For a given link, it returns all historical TWITTER interactions,
    associated with the link.
    Warning: To be able to run the following code, one must have an approved
    Academic Reasearch Account In Twitter! Also the BEARER_TOKEN, which is the
    access token to Twitter's Api, has to be in the file as this script.
    Params:
    -----------
    ** url (str): Link we want to retrieve engagements from
    Output:
    -----------
    ** df: Dataframe with all variables associated to the interaction the link
    had in Twitter.
    """
    def __init__(self,
                 url,
                 BEARER_TOKEN,
                 column_link,
                 start_time = "2006-03-26T00:00:00Z",
                 end_time = str(date.today())+'T00:00:00Z'):
                 self.bearer_token = BEARER_TOKEN
                 self.search_url = "https://api.twitter.com/2/tweets/search/all"
                 self.url = url
                 self.start_time = start_time
                 self.end_time = end_time
                 self.column_link = column_link

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, url, headers, params):
        time.sleep(1)
        while True:
            try:
                response = requests.get(self.search_url,
                                        headers = headers,
                                        params = params)
            except response.status_code != 200:
                time.sleep(60)
                continue
            break
        return response.json()

    def paginate(self, json_response, query_params):
        next_token = json_response["meta"]["next_token"]
        query_params.update({'next_token': next_token})

    def twitter_df(self):
         """
         Creates blank dataframe of stats associated to a link/tweet/conversation_id shared through
         Twitter's api.
         """
         df_stats= pd.DataFrame(columns =  ['author_id', 'created_at',
         'entities.annotations', 'entities.hashtags',
          'entities.mentions', 'entities.urls', 'id', 'lang',
          'possibly_sensitive', 'public_metrics.like_count',
          'public_metrics.quote_count', 'public_metrics.reply_count',
          'public_metrics.retweet_count', 'referenced_tweets', 'reply_settings',
          'source', 'text', self.column_link,
          'date_consulted'])
         return(df_stats)

    def main(self):
        headers = self.create_headers(self.bearer_token)

        query_params = {'query': '(url:"'+ self.url+'")',
                        'tweet.fields': 'created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
                        'user.fields':'description',
                        'max_results': 500,
                        'expansions' : 'author_id',
                        'media.fields' : 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width',
                        "start_time": self.start_time,
                        "end_time": self.end_time}

        json_response = self.connect_to_endpoint(self.search_url,
                                                 headers,
                                                 query_params)
        try:
            df = json_normalize(json_response['data'])
            df = df.sort_index(axis=1)
            while 'next_token' in json_response['meta'].keys():
                time.sleep(1)
                self.paginate(json_response, query_params)
                response = requests.get(self.search_url,
                                        headers=headers,
                                        params=query_params)
                json_response.update(response.json())
                flat = json_normalize(json_response['data'])
                flat = flat.sort_index(axis=1)
                df = df.append(flat)
            df.reset_index(drop=True,
                           inplace=True)
        except:
            df = self.twitter_df()
            df = df.append(pd.Series(), ignore_index=True)
        df[self.column_link]=self.url
        df['date_consulted'] = str(date.today())
        return(df)


class GetTweetsFromUser:

    """For a given user-handle, it returns all tweets associated.
    Warning: To be able to run the following code, one must have an approved
    Academic Reasearch Account In Twitter! Also the BEARER_TOKEN, which is the
    access token to Twitter's Api, has to be in the file as this script.
    Params:
    -----------
    ** user (str): User handle.
    Output:
    -----------
    ** df: Dataframe with all tweets associated to the user-handle.
    """

    def __init__(self,
                 user,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.search_url = "https://api.twitter.com/2/tweets/search/all"
                 self.user = user

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, url, headers, params):
        time.sleep(1)
        response = requests.get(self.search_url,
                                headers = headers,
                                params = params)

        json_response = response.json()
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return json_response

    def paginate(self, json_response, query_params):
        next_token = json_response["meta"]["next_token"]
        query_params.update({'next_token': next_token})

    def main(self):
        headers = self.create_headers(self.bearer_token)

        query_params = {'query': '(from:'+ self.user+')',
                        'tweet.fields': 'created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
                        'user.fields':'description',
                        'max_results': 500,
                        'expansions' : 'attachments.poll_ids,attachments.media_keys,author_id,geo.place_id,in_reply_to_user_id,referenced_tweets.id,entities.mentions.username,referenced_tweets.id.author_id',
                        'media.fields' : 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width',
                        "start_time": "2020-11-01T00:00:00Z",
                        "end_time": str(date.today())+'T00:00:00Z'}

        json_response = self.connect_to_endpoint(self.search_url,
                                                 headers,
                                                 query_params)

        df = json_normalize(json_response['data'])
        df = df.sort_index(axis=1)

        while 'next_token' in json_response['meta'].keys():
            time.sleep(1)
            self.paginate(json_response, query_params)
            response = requests.request("GET", self.search_url,
                                               headers=headers,
                                               params=query_params)
            json_response.update(response.json())
            flat = json_normalize(json_response['data'])
            flat = flat.sort_index(axis=1)
            df = df.append(flat)

        df['date_consulted'] = str(date.today())
        df.reset_index(drop=True,
                       inplace=True)
        return(df)


class GetStatsFromTweets():

    """
    Retrieves stats associated to a list of tweets.
    Params:
    -----------
    ** tweets_ids (list): Twitter ids we want to retrieve engagements from.
                          List of max 100 ids.
    Output:
    -----------
    ** data: Json object with the result of the call to the api.
    """
    def __init__(self,
                 tweets_ids,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.tweets_ids = tweets_ids
                 self.params = {
                                'tweet.fields':'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
                                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
                                'media.fields': 'duration_ms,height,media_key,non_public_metrics,organic_metrics,preview_image_url,promoted_metrics,public_metrics,type,url,width',
                                'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type'
                               }


    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, tweets_ids):
        time.sleep(1)
        url="https://api.twitter.com/2/tweets?ids={}".format(",".join(tweets_ids))
        response = requests.get(url,
                                headers = headers,
                                params= self.params)
        return(response.json())

    def main(self):
        headers=self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.tweets_ids)
        data=json_normalize(data['data'])
        data['date_consulted'] = str(date.today())
        return(data)


class GetStatsFromTweet():

    """
    Retrieves stats associated to an specific tweet. This is restricted to 500
    calls per 15 minutes.
    Params:
    -----------
    ** tweet_id (str): Twitter id we want to retrieve engagements from
    Output:
    -----------
    ** data: Json object with the result of the call to the api.
    """
    def __init__(self,
                 tweet_id,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.tweet_id = tweet_id
                 self.params = {
                                'tweet.fields':'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
                                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
                                'media.fields': 'duration_ms,height,media_key,non_public_metrics,organic_metrics,preview_image_url,promoted_metrics,public_metrics,type,url,width',
                                'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type'
                               }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, tweet_id):
        time.sleep(1)
        response = requests.get("https://api.twitter.com/2/tweets/{}".format(tweet_id),
                                headers = headers,
                                params= self.params)
        return(response.json())

    def main(self):
        headers=self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.tweet_id)
        data = json_normalize(data)
        data['date_consulted'] = str(date.today())
        return(data)


class GetStatsFromUsers():

    """
    Retrieves information from a list of twitter accounts. This is restricted to 500
    calls per 15 minutes.
    Params:
    -----------
    ** user_ids (list): List of twitter ids we want to retrieve engagements from
    Output:
    -----------
    ** data: Json object with the result of the call to the api.
    """

    def __init__(self,
                 user_ids,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.user_ids = user_ids
                 self.params = {
                                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                               }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, user_ids):
        time.sleep(1)
        response = requests.get("https://api.twitter.com/2/users?ids={}".format(",".join(user_ids)),
                                headers = headers,
                                params= self.params)
        return(response.json())

    def main(self):
        headers=self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.user_ids)
        data=json_normalize(data['data'])
        return(data)


class GetStatsFromUser():

    """
    Retrieves stats associated to an specific tweet. This is restricted to 500
    calls per 15 minutes.
    Params:
    -----------
    ** tweet_id (str): Twitter id we want to retrieve engagements from
    Output:
    -----------
    ** data: Json object with the result of the call to the api.
    """

    def __init__(self,
                 user_id,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.user_id = user_id
                 self.params = {
                                'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
                               }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, user_id):
        time.sleep(1)
        response = requests.get("https://api.twitter.com/2/users/{}".format(user_id),
                                headers = headers,
                                params= self.params)
        return(response.json())

    def main(self):
        headers=self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.user_id)
        return(data)


class GetRepliesAssociatedToTweet:

    """It returns all historical `replies` associated with a given `conversation_id`
    Warning: To be able to run the following code, one must have an approved
    Academic Reasearch Account In Twitter! Also the BEARER_TOKEN, which is the
    access token to Twitter's Api, has to be in the file as this script.
    Params:
    -----------
    ** conversation_id (str): conversation_id from which we want to retrieve replies
    from
    Output:
    -----------
    ** df: dataframe with all variables associated to the replies associated to a
    conversation_id
    """
    def __init__(self,
                 conversation_id,
                 BEARER_TOKEN):
                 self.bearer_token = BEARER_TOKEN
                 self.search_url = "https://api.twitter.com/2/tweets/search/all"
                 self.conversation_id = conversation_id

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, url, headers, params):
        time.sleep(1)
        while True:
            try:
                response = requests.get(self.search_url,
                                        headers = headers,
                                        params = params)
            except response.status_code != 200:
                time.sleep(60)
                continue
            break
        return response.json()

    def paginate(self, json_response, query_params):
        next_token = json_response["meta"]["next_token"]
        query_params.update({'next_token': next_token})

    def main(self):
        headers = self.create_headers(self.bearer_token)

        query_params = {'query' :'conversation_id:'+ str(self.conversation_id),
                        'tweet.fields': 'created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
                        'user.fields':'description',
                        'max_results': 500,
                        'expansions' : 'author_id',
                        'media.fields' : 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width',
                        "start_time": "2006-03-26T00:00:00Z",
                        "end_time": str(date.today())+'T00:00:00Z'}

        json_response = self.connect_to_endpoint(self.search_url,
                                                 headers,
                                                 query_params)
        try:
            df = json_normalize(json_response['data'])
            df = df.sort_index(axis=1)
            while 'next_token' in json_response['meta'].keys():
                time.sleep(1)
                self.paginate(json_response, query_params)
                response = requests.get(self.search_url,
                                        headers=headers,
                                        params=query_params)
                json_response.update(response.json())
                flat = json_normalize(json_response['data'])
                flat = flat.sort_index(axis=1)
                df = df.append(flat)
            df.reset_index(drop=True,
                           inplace=True)
            df['date_consulted'] = str(date.today())
            return(df)
        except:
            pass
