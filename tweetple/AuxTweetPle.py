# ============================================================================

# Auxiliar functions

# ============================================================================
import math
import pandas as pd

from functools import reduce


def twitter_df(column_link):
    """
    Creates blank dataframe of stats associated to a link/tweet/conversation_id shared through
    Twitter's api.
    """
    df_stats = pd.DataFrame(
        columns=['author_id', 'created_at',
                 'entities.annotations', 'entities.hashtags',
                 'entities.mentions', 'entities.urls', 'id', 'lang',
                 'possibly_sensitive', 'public_metrics.like_count',
                 'public_metrics.quote_count', 'public_metrics.reply_count',
                 'public_metrics.retweet_count', 'conversation_id',
                 'referenced_tweets', 'reply_settings',
                 'source', 'text', column_link,
                 'date_consulted'])
    return df_stats


def roundup(x):
    """Rounds up to the next nearest 100"""

    return int(math.ceil(x / 100.0)) * 100


def df_tweets_stats():
    """
    Creates blank dataframe of stats associated to a **LIST OF TWEETS** shared through
    Twitter's api.
    """
    df_stats = pd.DataFrame(
        columns=['created_at', 'possibly_sensitive', 'id', 'reply_settings',
                 'conversation_id', 'lang', 'text', 'conversation_id',
                 'source', 'author_id', 'public_metrics.retweet_count',
                 'public_metrics.reply_count', 'public_metrics.like_count',
                 'public_metrics.quote_count', 'in_reply_to_user_id',
                 'referenced_tweets', 'entities.mentions', 'entities.hashtags',
                 'entities.annotations', 'entities.urls', 'attachments.media_keys',
                 'date_consulted']
    )
    return df_stats


def df_users_stats():
    """
    Creates blank dataframe of stats associated to a **LIST OF TWEETS** shared through
    Twitter's api.
    """
    df_stats = pd.DataFrame(
        columns=['location', 'profile_image_url', 'protected', 'username', 'id',
                 'verified', 'description', 'created_at', 'name', 'url',
                 'public_metrics.followers_count', 'public_metrics.following_count',
                 'public_metrics.tweet_count', 'public_metrics.listed_count',
                 'pinned_tweet_id', 'entities.url.urls', 'entities.description.mentions',
                 'entities.description.urls', 'entities.description.hashtags']
    )

    return df_stats


def aggregate_twitter_metrics(df, column):
    """Computes aggregated Twitter metrics from disaggregated metrics

    Parameters
    ----------
    df : dataframe
        Dataframe with disaggregated metrics
    column : str
        Column with links searched

    Returns
    -------
    engagements : dataframe
        Dataframe with aggregated engagement metrics
    """

    df['shared'] = df['id'].notna().astype(int)
    shared_twitter = df[[column, 'shared']].drop_duplicates()
    metrics_columns = [col for col in df.columns if 'public_metrics' in col]
    df[metrics_columns] = df[metrics_columns].fillna(value=0)
    metrics = df.groupby(column).sum().reset_index().drop(columns='shared')
    num_users = df[df.shared == 1].groupby([column]).count().reset_index()
    num_users = num_users.rename(columns={'author_id': 'num_users'})
    engagements = reduce(
        lambda left, right: pd.merge(left, right, on=column, how='left'),
        [shared_twitter, metrics, num_users[[column, 'num_users']]]
    )
    engagements["total_interactions"] = engagements[
        [x for x in engagements.columns if 'public_metrics' in x]
    ].sum(axis="columns")
    engagements.columns = engagements.columns.str.replace(
        'public_metrics.', '')
    engagements['n_calls'] = df['response']/200
    cols = [str(col) + '_twitter' for col in engagements.columns if col != column]
    engagements.columns = [column] + cols

    return engagements.fillna(0)
