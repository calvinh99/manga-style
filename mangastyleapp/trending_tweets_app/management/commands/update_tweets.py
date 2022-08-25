from django.core.management.base import BaseCommand, CommandError
from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment
from django.utils import timezone
from django.utils.timezone import make_aware

import os
from pathlib import Path
from dotenv import load_dotenv

import time
import requests
from datetime import datetime

from .add_new_twitter_artists import save_artist_data

# /Users/calvinhuang/ml/mangastyle/mangastyleapp/trending_tweets_app
APP_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(APP_DIR / '.env')

bearer_token = os.environ.get("BEARER_TOKEN")

def bearer_oauth(r):
    r.headers["Authorization"] = "Bearer {}".format(bearer_token)
    return r

def get_request(url):
    response = requests.get(url, auth=bearer_oauth)
    if response.status_code != 200:
        raise ValueError("API call did not succeed, http response: {}".format(response.json()))
    return response.json()

def get_recent_media_tweets(username):
    url = ("https://api.twitter.com/2/tweets/search/recent"
           "?query=from%3A{}%20(has%3Amedia%20-is%3Aretweet%20-is%3Areply%20-is%3Aquote%20%20-has%3Avideos)"
           "&max_results=100"
           "&sort_order=recency"
           "&tweet.fields=id,text,public_metrics,created_at,lang,attachments,possibly_sensitive"
           "&expansions=attachments.media_keys,author_id"
           "&media.fields=media_key,type,url"
           "&user.fields=id,profile_image_url,public_metrics,username"
           .format(username))
    return get_request(url)

def save_tweet_data(tweet_data, artist):
    try:
        tweet = MediaTweet.objects.get(tweet_id=tweet_data['id'])
        tweet.text = ''     # TODO: test out MySQL utf8mb4 for multi-language and emojis
        tweet.likes_count = tweet_data['public_metrics']['like_count']
        tweet.retweets_count = tweet_data['public_metrics']['retweet_count']
        tweet.possibly_sensitive = tweet_data['possibly_sensitive']
        tweet.save()
    except MediaTweet.DoesNotExist:
        created_at = make_aware(datetime.strptime(tweet_data['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        tweet = MediaTweet(tweet_id=tweet_data['id'],
                           text='',     # TODO: test out MySQL utf8mb4 for multi-language and emojis
                           likes_count=tweet_data['public_metrics']['like_count'],
                           retweets_count=tweet_data['public_metrics']['retweet_count'],
                           created_at=created_at,
                           lang=tweet_data['lang'],
                           possibly_sensitive=tweet_data['possibly_sensitive'],
                           author=artist)
        tweet.save()
    except Exception as e:
        raise CommandError('Something went wrong for tweet {}: {}'.format(tweet_data['id'], e))
    return tweet

def save_media_data(media_data, tweet):
    try:
        media = MediaAttachment.objects.get(media_id=media_data['media_key'])
        media.style = ''
        media.parent_tweet = tweet
        media.save()
    except MediaAttachment.DoesNotExist:
        media = MediaAttachment(media_id=media_data['media_key'],
                                media_url=media_data['url'],
                                media_type=media_data['type'],
                                media_style='',
                                parent_tweet=tweet)
        media.save()
    except Exception as e:
        raise CommandError('Something went wrong for media {}: {}'.format(media_data['url'], e))
    return media

def update_artist(username):
    try:
        json_response = get_recent_media_tweets(username)
        result_count = json_response['meta']['result_count']
        if result_count == 0:
            artist = TwitterArtist.objects.get(username=username)
            artist.save()
            return result_count
        artist = save_artist_data(json_response['includes']['users'][0], update_existing=True)

        media_id_map = {media_dict['media_key']: media_dict 
                        for media_dict in json_response['includes']['media']}

        for tweet_data in json_response['data']:
            tweet = save_tweet_data(tweet_data, artist)

            media_ids = tweet_data['attachments']['media_keys']
            for media_id in media_ids:
                media_data = media_id_map[media_id]
                save_media_data(media_data, tweet)
    except ValueError as ve:
        raise CommandError("Error {} for artist {}.".format(ve, username))
    return result_count

def log_update(username, self):
    self.stdout.write("Updating artist {}".format(username), ending=' ... ')
    self.stdout.flush()
    time.sleep(0.01)

    try:
        result_count = update_artist(username)

        self.stdout.write(self.style.SUCCESS("Updated artist {} with {} tweets."
                                             .format(username, result_count)))
        self.stdout.flush()
        time.sleep(0.01)
    except Exception as e:
        self.stdout.write(self.style.ERROR("Error updating artist {}: {}".format(username, e)))
        self.stdout.flush()
        time.sleep(0.01)

class Command(BaseCommand):
    help = "Update the user data, recent tweets, and media attachments of all saved twitter artists."

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)

    def handle(self, *args, **options):
        if options['usernames'][0] == 'all':
            self.stdout.write("Updating all artists", ending='\n{}\n'.format('-'*40))
            self.stdout.flush()
            time.sleep(0.01)

            for artist in TwitterArtist.objects.all().order_by('last_updated'):
                log_update(artist.username, self)

            self.stdout.write(self.style.SUCCESS("Updated all artists."))
        else:
            for username in options['usernames']:
                log_update(username, self)