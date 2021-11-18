# TWEETPLE
![GitHub all releases](https://img.shields.io/github/downloads/dapivei/tweetple/total?color=84A3BC&logo=Github)
[![Twitter API v2 badge](https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2)](https://developer.twitter.com/en/docs/twitter-api/early-access)
## Installation

The easiest way to install the latest version from PyPI is by using pip:
```python
pip install tweetple
```

## Usage

+ Retrieve tweeplers' timeline information

```python
import tweetple

from tweetple import TweetPle

# bearer token accesible via Twitter Developer Academic Research Track
bearer_token='AAAAAAAA'
# list of tweeplers' ids
ids = ['308131814']
TweetPle.TweepleStreamer(ids, bearer_token).main()

```

+ Retrieve tweets

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
