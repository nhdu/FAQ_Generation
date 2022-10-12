import snscrape.modules.twitter as sntwitter
import pandas as pd

class TwitterFeeds:
    def get_feeds(self, query: str, limit: int):
        tweets = []
        for tweet in sntwitter.TwitterSearchScraper(query).get_items():
            if (len(tweets) == limit):
                break
            else:
                tweets.append([tweet.date, tweet.user.username, tweet.content])
        df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
        return list(df['Tweet']) 
    
# tweet = TwitterFeeds()
# pd = tweet.get_feeds("Python programming min_faves:1000 lang:en", 300)
# print(pd)
