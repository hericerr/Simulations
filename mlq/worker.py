"""
Worker taking jobs from redis and applying VADER model to the texts
"""
import time
import asyncio

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from mlq.queue import MLQ

# redis queue - assumes redis already running on port 6379
mlq = MLQ('anakin', 'localhost', 6379, 0)

# download and initialize model
nltk.download('vader_lexicon')
darth_vader = SentimentIntensityAnalyzer()


def analyze(param_dict, *args):
    time.sleep(0.5) # pretend to work a little harder
    return darth_vader.polarity_scores(param_dict['text'])


async def main():
    print("Running, waiting for messages.")
    mlq.create_listener(analyze)


if __name__ == '__main__':
    asyncio.run(main())