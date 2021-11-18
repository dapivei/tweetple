# TWEETPLE
![GitHub all releases](https://img.shields.io/github/downloads/dapivei/tweetple/total?color=84A3BC&logo=Github)

## Installation

The easiest way to install the latest version from PyPI is by using pip:
```python
pip install tweetple
```

## Usage

+ Retrieve tweeplers timeline information 

```python
import tweetple

from tweetple import TweetPle

# bearer token accesible via Twitter Developer Academic Research Track
bearer_token='AAAAAAAA'
# list of tweeplers' ids
ids = ['308131814']
TweetPle.TweepleStreamer(ids, bearer_token).main()

```

+ Retrieve tweets either by providing directly a list of Tweets's ids we want to collect or by providing the twitter handle name of twitter accounts we want to collect tweets from.

```python
import tweetple

from tweetple import TweetPle

# bearer token accesible via Twitter Developer Academic Research Track
bearer_token='AAAAAAAA'
# list of tweets' ids
tweetids = ['1461090445702881281']
TweetPle.TweetStreamer(tweetids, bearer_token, handles=False, file_name='tweets').main()

# list of tweeplers' twitter handles
tweephandles = ['zorroyanez']
TweetPle.TweetStreamer(tweephandles, bearer_token ).main()

```
