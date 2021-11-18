# ============================================================================

# Auxiliar functions

# ============================================================================
import math
import pandas as pd

def twitter_df(column_link):
    """
    Creates blank dataframe of stats associated to a link/tweet/conversation_id shared through
    Twitter's api.
    """
    df_stats= pd.DataFrame(
        columns =  ['author_id', 'created_at',
                    'entities.annotations', 'entities.hashtags',
                    'entities.mentions', 'entities.urls', 'id', 'lang',
                    'possibly_sensitive', 'public_metrics.like_count',
                    'public_metrics.quote_count', 'public_metrics.reply_count',
                    'public_metrics.retweet_count', 'referenced_tweets', 'reply_settings',
                    'source', 'text', column_link,
                    'date_consulted'])
    return(df_stats)


def roundup(x):
    """Rounds up to the next nearest 100"""
    return int(math.ceil(x / 100.0)) * 100


def df_tweets_stats():
    """
    Creates blank dataframe of stats associated to a **LIST OF TWEETS** shared through
    Twitter's api.
    """
    df_stats= pd.DataFrame(
        columns = ['created_at', 'possibly_sensitive', 'id', 'reply_settings',
       'conversation_id', 'lang', 'text', 'context_annotations', 'source',
       'author_id', 'public_metrics.retweet_count',
       'public_metrics.reply_count', 'public_metrics.like_count',
       'public_metrics.quote_count', 'in_reply_to_user_id',
       'referenced_tweets', 'entities.mentions', 'entities.hashtags',
       'entities.annotations', 'entities.urls', 'attachments.media_keys',
       'date_consulted']
    )
    return(df_stats)


def df_users_stats():
    """
    Creates blank dataframe of stats associated to a **LIST OF TWEETS** shared through
    Twitter's api.
    """
    df_stats= pd.DataFrame(
        columns = ['location', 'profile_image_url', 'protected', 'username', 'id',
       'verified', 'description', 'created_at', 'name', 'url',
       'public_metrics.followers_count', 'public_metrics.following_count',
       'public_metrics.tweet_count', 'public_metrics.listed_count',
       'pinned_tweet_id', 'entities.url.urls', 'entities.description.mentions',
       'entities.description.urls', 'entities.description.hashtags']
    )
    return(df_stats)


def aggregated_stats_twitter(df, column_link):

    """Converts disaggregated twitter stats to aggregated twitter stats"""

    df['shared_twitter']=df['id'].notna().astype(int)
    shared_twitter = df[[column_link,'shared_twitter']]
    shared_twitter = shared_twitter.drop_duplicates()
    columns =['public_metrics.like_count', 'public_metrics.quote_count', 'public_metrics.reply_count', 'public_metrics.retweet_count']
    df[columns]=df[columns].fillna(value=0)
    metrics = df.groupby(column_link).sum().reset_index()
    metrics=metrics[metrics.columns[:-1]]
    metrics = metrics.rename(
    columns={
    'public_metrics.like_count': 'like_count_twitter',
    'public_metrics.quote_count': 'quote_count_twitter',
    'public_metrics.reply_count':'reply_count_twitter',
    'public_metrics.retweet_count':'retweet_count_twitter'
    })
    df_agg=shared_twitter.merge(metrics, how='left', on=column_link)
    not_nas = df[df.shared_twitter==1]
    num_users = not_nas.groupby([column_link]).count().reset_index()
    num_users= num_users[[column_link, 'author_id' ]]
    num_users = num_users.rename(
    columns={
    'author_id': 'num_users_twitter'
    })
    df_agg=df_agg.merge(num_users, how='left', on=column_link)
    df_agg['total_interactions_twitter']= df_agg['like_count_twitter']+df_agg['quote_count_twitter']+df_agg['reply_count_twitter']+df_agg['retweet_count_twitter']
    return(df_agg.fillna(0))
