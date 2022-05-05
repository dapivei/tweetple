# ============================================================================

# Classes to retrieve data from Twitters "Full-Archive Search" Endpoint

# ============================================================================

import requests
import pandas as pd
import time

from tqdm import tqdm
from pandas import json_normalize
from datetime import date


class TwitterObject:

    """Generic class to represent a Twitter object

    ...
    Attributes
    ----------
    bearer_token : str
        credentials for the Twitter developer app
    search_url : str
        name of column in which the link will be stored
    start_time : datetime
        start date of scrape
    end_time : datetime
        end date of scrape
    search_url : str
        endpoint we want to retrieve information from

    Methods
    -------
    create_headers()
        Executes query
    connect_to_endpoint()
        Connects to Twitter's endpoint
    paginate()
        Pagines
    query()
        Defines the query's parameters
    call()
        Api call   

    """

    def __init__(self, bearer_token, start_time, end_time, search_url):
        """
        Initialize the object's attributes
        """
        self.bearer_token = bearer_token
        self.search_url = search_url
        self.start_time = start_time
        self.end_time = end_time

    def create_headers(self):
        """
        Create headers for call
        """
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}

        return headers

    def connect_to_endpoint(self, headers, params):
        """
        Connect to Twitters's endpoint
        """
        time.sleep(1)

        while True:

            try:

                response = requests.get(

                    self.search_url,
                    headers=headers,
                    params=params

                )

            except response.status_code != 200:

                time.sleep(60)

                continue

            break

        return response

    def paginate(self, json_response, query_params):
        """
        Paginate through searches
        """

        next_token = json_response["meta"]["next_token"]

        query_params.update({'next_token': next_token})

    def query(self):

        query = {
            'tweet.fields': 'author_id,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified',
            'max_results': 500,
            'expansions': 'attachments.poll_ids,attachments.media_keys,author_id,geo.place_id,in_reply_to_user_id,referenced_tweets.id,entities.mentions.username,referenced_tweets.id.author_id',
            'media.fields': 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width',
            'start_time': self.start_time,
            'end_time': self.end_time

        }

        return query

    def call(self, json_response, query, headers):

        df = json_normalize(json_response['data']).sort_index(axis=1)

        while 'next_token' in json_response['meta'].keys():

            time.sleep(1)

            self.paginate(json_response, query)

            response = requests.request(

                "get",
                self.search_url,
                headers=headers,
                params=query

            )

            json_response.update(response.json())

            df = df.append(
                json_normalize(json_response['data']).sort_index(axis=1)
            )

        df.reset_index(

            drop=True,
            inplace=True

        )

        return df


class GetInteractionsAssociatedToLink(TwitterObject):

    """Historical Twitter interactions associated to a link.

    ...

    Attributes
    ----------
    url : str
        link we want to retrieve engagements from
    column_link : str
        name of column in which the link will be stored
    start_time : datetime
        start date of scrape
    end_time : datetime
        end date of scrape
    bearer_token : str
        bearer token
    search_url : str
        endpoint we want to retrieve information from

    Methods
    -------
    main()
        Executes query
    create_dataframe()
        Creates empty dataframe
    """

    def __init__(self, url, bearer_token, column_link, start_time, end_time,  search_url):
        """
        Parameters
        ----------
        url : str
            url to search for
        bearer_token : str
            bearer token
        column_link : str
            column containing the link
        start_time : timestamp
            earliest date to retrieve data from
        end_time : timestamp
            latest date to retrieve data from
        """

        super().__init__(bearer_token, start_time, end_time, search_url)
        self.url = url
        self.column_link = column_link

    def create_dataframe(self):
        """Creates blank dataframe of stats retrieved from Twitter's API.

        Returns
        -------
        dataframe
            A empty dataframe
        """
        stats = pd.DataFrame(
            columns=[
                'author_id', 'created_at', 'entities.annotations', 'entities.hashtags', 'entities.mentions', 'entities.urls', 'id', 'lang', 'possibly_sensitive', 'public_metrics.like_count', 'public_metrics.quote_count',  'public_metrics.reply_count', 'public_metrics.retweet_count', 'referenced_tweets', 'reply_settings', 'source', 'text', self.column_link, 'date_consulted'
            ]
        )

        return stats

    def main(self):
        """Executes query to Twitter's API.

        Returns
        -------
        dataframe
            A dataframe with engagement metrics associated to searched link
        """
        headers = self.create_headers()

        query = {

            **{"query": '(url:"' + self.url+'")'},
            **self.query()

        }
        response = self.connect_to_endpoint(

            headers,
            query

        )

        json_response = response.json()

        try:

            df = self.call(json_response, query, headers)

        except:

            df = self.create_dataframe()

            df = df.append(pd.Series(), ignore_index=True)

        df[self.column_link], df['date_consulted'], df['response'] = self.url, str(
            date.today()), response.status_code

        return df


class GetFollowers:

    """Get Followers from an specific Twitter user
    This call is restricted to 15 calls every 15 minutes.

    Attributes
    ----------
    id_user : str
        List of ids we want to retrieve information from
    bearer_token : str
        Bearer token

    Methods
    -------
    main()
        Execute call to retrieve followers
    """

    def __init__(self, id_user, bearer_token):

        self.bearer_token = bearer_token
        self.id_user = id_user
        self.search_url = "https://api.twitter.com/2/users/{}/followers".\
            format(
                id_user
            )

    def main(self):

        query = {'max_results': 1000, 'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'}

        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}

        response = requests.get(
            self.search_url,
            headers=headers,
            params=query
        )
        json_response = response.json()

        df = pd.DataFrame(json_response['data']).sort_index(axis=1)

        while 'next_token' in json_response['meta'].keys():

            time.sleep(60)

            next_token = json_response["meta"]["next_token"]

            query.update({'pagination_token': str(next_token)})

            response = requests.get(

                self.search_url,
                headers=headers,
                params=query

            )

            json_response.update(response.json())

            df = df.append(pd.DataFrame(
                json_response['data']).sort_index(axis=1))

        df.reset_index(

            drop=True,
            inplace=True

        )

        df['author_id_following'], df['date_consulted'], df['response'] = self.id_user, str(
            date.today()), response.status_code

        return df


class GetTweetplerInteracting:
    """Retrieves a list of accounts that have liked or retweeted a Tweet."""

    def __init__(self, id_tweet, bearer_token, type_interaction):
        self.id_tweet = id_tweet
        self.type = type_interaction
        self.bearer_token = bearer_token

    def main(self):

        if self.type == 'liking_users':
            end = 'liking_users'
            col = 'tweet_liked'
        else:
            end = 'retweeted_by'
            col = 'tweet_retweeted'

        url = "https://api.twitter.com/2/tweets/{}/{}".format(
            self.id_tweet, end)
        query = {'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'}

        response = requests.get(
            url,
            headers={"Authorization": "Bearer {}".format(self.bearer_token)},
            params=query
        )

        response_status = [response.status_code]

        json_response = response.json()

        df = pd.DataFrame(json_response['data']).sort_index(axis=1)

        time.sleep(11)

        while 'next_token' in json_response['meta'].keys():
            next_token = json_response["meta"]["next_token"]
            query.update({'pagination_token': str(next_token)})
            response = requests.get(

                url,
                headers={"Authorization": "Bearer {}".format(
                    self.bearer_token)},
                params=query

            )

            response_status[0] = [
                response.status_code if response.status_code != 200 else response_status[0]][0]

            json_response.update(response.json())

            try:
                df = df.append(pd.DataFrame(
                    response.json()['data']).sort_index(axis=1))
            except:
                pass

            time.sleep(11)

        df.reset_index(

            drop=True,
            inplace=True

        )
        df[col], df['date_consulted'], df['response'] = self.id_tweet, str(
            date.today()), response_status[0]

        return df


class GetTweetsFromUser(TwitterObject):

    """Historical Tweets from Twitter user

    ...

    Attributes
    ----------
    user : str
        user's handle
    search_url : str
        endpoint we want to retrieve information from
    start_time : datetime
        start date of scrape
    end_time :datetime
        end date of scrape
    bearer_token : str
        bearer token


    Methods
    -------
    main()
        Executes query

    """

    def __init__(self, user, bearer_token, start_time, end_time, search_url):
        """
        Parameters
        ----------
        user : str
            user's handle
        search_url : str
            name of column in which the link will be stored
        start_time : datetime
            start date of scrape
        end_time :datetime
            end date of scrape
        bearer_token : str
            bearer token
        """
        super().__init__(bearer_token, start_time, end_time, search_url)
        self.user = user

    def main(self):
        """Executes query to Twitter's API.

        Returns
        -------
        dataframe
            A dataframe with Tweets twitted by user
        """
        headers = self.create_headers()

        query = {

            **{"query": '(from:' + self.user+')'},
            **self.query()

        }

        response = self.connect_to_endpoint(

            headers,
            query

        )

        json_response = response.json()

        df = self.call(json_response, query, headers)

        df['handle'], df['date_consulted'], df['response'] = self.user, str(
            date.today()), response.status_code

        df = df.drop_duplicates(subset='id').reset_index(drop=True)

        return df


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

    def __init__(self, tweets_ids, bearer_token):
        self.bearer_token = bearer_token
        self.tweets_ids = tweets_ids
        self.params = {
            'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
            'media.fields': 'duration_ms,height,media_key,non_public_metrics,organic_metrics,preview_image_url,promoted_metrics,public_metrics,type,url,width',
            'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type'
        }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, tweets_ids):
        time.sleep(1)
        url = "https://api.twitter.com/2/tweets?ids={}".format(
            ",".join(tweets_ids))
        response = requests.get(
            url,
            headers=headers,
            params=self.params
        )
        return(response.json())

    def main(self):
        headers = self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.tweets_ids)
        data = json_normalize(data['data'])
        data['date_consulted'] = str(date.today())
        return data


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

    def __init__(self, tweet_id, bearer_token):
        self.bearer_token = bearer_token
        self.tweet_id = tweet_id
        self.params = {
            'tweet.fields': 'attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld',
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld',
            'media.fields': 'duration_ms,height,media_key,non_public_metrics,organic_metrics,preview_image_url,promoted_metrics,public_metrics,type,url,width',
            'place.fields': 'contained_within,country,country_code,full_name,geo,id,name,place_type'
        }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, tweet_id):
        time.sleep(1)
        response = requests.get(
            "https://api.twitter.com/2/tweets/{}".format(tweet_id),
            headers=headers,
            params=self.params
        )
        return response.json()

    def main(self):
        headers = self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.tweet_id)
        data = json_normalize(data)
        data['date_consulted'] = str(date.today())

        return data


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

    def __init__(self, user_ids, bearer_token):
        self.bearer_token = bearer_token
        self.user_ids = user_ids
        self.params = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
        }

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, user_ids):
        time.sleep(1)
        response = requests.get(
            "https://api.twitter.com/2/users?ids={}".format(
                ",".join(user_ids)),
            headers=headers,
            params=self.params
        )
        return response.json()

    def main(self):
        headers = self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.user_ids)
        data = json_normalize(data['data'])
        return data


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

    def __init__(self, user_id, bearer_token):
        self.bearer_token = bearer_token
        self.user_id = user_id
        self.params = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'}

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, headers, user_id):
        time.sleep(1)
        response = requests.get(
            "https://api.twitter.com/2/users/{}".format(user_id),
            headers=headers,
            params=self.params
        )
        return response.json()

    def main(self):
        headers = self.create_headers(self.bearer_token)
        data = self.connect_to_endpoint(headers, self.user_id)
        return data


class GetRepliesAssociatedToTweet:

    """Builds conversation threads from an specific conversation id
    ...

    Attributes
    ----------
    conversation_id : str
        id of conversation thread we want to build
    bearer_token : str
        credentials for the Twitter developer app

    Methods
    ----------

    """

    def __init__(self, conversation_id, bearer_token):
        self.bearer_token = bearer_token
        self.search_url = "https://api.twitter.com/2/tweets/search/all"
        self.conversation_id = conversation_id

    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(self.bearer_token)}
        return headers

    def connect_to_endpoint(self, url, headers, params):
        time.sleep(1)
        while True:
            try:
                response = requests.get(
                    self.search_url,
                    headers=headers,
                    params=params
                )
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

        query_params = {'query': 'conversation_id:' + str(self.conversation_id),
                        'tweet.fields': 'author_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,text,possibly_sensitive,referenced_tweets,reply_settings,source',
                        'max_results': 500,
                        'expansions': "author_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,attachments.poll_ids,attachments.media_keys,geo.place_id",
                        'media.fields': 'duration_ms,height,media_key,preview_image_url,public_metrics,type,url,width',
                        "start_time": "2021-01-26T00:00:00Z",
                        "end_time": str(date.today())+'T00:00:00Z'}

        json_response = self.connect_to_endpoint(
            self.search_url,
            headers,
            query_params
        )
        try:
            df = json_normalize(json_response['data'])
            df = df.sort_index(axis=1)
            while 'next_token' in json_response['meta'].keys():
                time.sleep(1)
                self.paginate(json_response, query_params)
                response = requests.get(
                    self.search_url,
                    headers=headers,
                    params=query_params
                )
                json_response.update(response.json())
                flat = json_normalize(json_response['data'])
                flat = flat.sort_index(axis=1)
                df = df.append(flat)
            df.reset_index(
                drop=True,
                inplace=True
            )
            df['date_consulted'] = str(date.today())
            df['conversation_id'] = self.conversation_id

            return df

        except:
            pass
