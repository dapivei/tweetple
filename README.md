# TWEETPLE

[![Twitter API v2 badge](https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2)](https://developer.twitter.com/en/docs/twitter-api/early-access)

## Installation

The easiest way to install the latest version from PyPI is by using pip:
```python
pip install tweetple
```

## Usage

+ Users, Followers, Liking Users and Retweeted By Lookup

```python
import tweetple

from tweetple import TweetPle

# Bearer token accesible via Twitter Developer Academic Research Track
bearer_token='AAAAAAAA'

# List of handle ids
ids = ['308131814']

# Retrieve users' information
TweetPle.TweepleStreamer(ids, bearer_token).user_lookup()

# Retrieve followers' information
TweetPle.TweepleStreamer(ids, bearer_token).followers_lookup()

# List of tweet ids

ids = ['308131814']

# Retrieve liking users
TweetPle.TweepleStreamer(ids, bearer_token).likes_lookup()

# Retrieve retweeting users

TweetPle.TweepleStreamer(ids, bearer_token).retweet_lookup()
```

+ Retrieve Tweets

One can provide as input a **list** of:

1. Tweets' ids

2. Tweeples' handles

3. Links

```python
import tweetple

from tweetple import TweetPle

# bearer token accesible via Twitter Developer Academic Research Track
bearer_token='AAAAAAAA'

# list of tweets' ids
tweetl = ['1461090445702881281']
TweetPle.TweetStreamer(tweetl, bearer_token).main()

# list of tweeplers' handles
tweeplel = ['zorroyanez']
TweetPle.TweetStreamer(tweeplel, bearer_token).main()

# list of links potentially shared via twitter
linkl = ['https://lula.com.br/22-vitorias-judiciais-de-lula-inquerito-contra-filhos-e-encerrado-por-falta-de-provas/']
TweetPle.TweetStreamer(linkl, bearer_token).main()

```
