# Basic libs
import os
import time
import requests

# Load tokens
from pathlib import Path
from dotenv import load_dotenv

# Models
from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment
from django.core.management.base import CommandError

# Datetime conversion
from datetime import datetime as dt # distinguish btwn datetime and datetime.datetime
from django.utils import timezone
from django.utils.timezone import make_aware

# logging
import logging

log = logging.getLogger(__name__)

dt_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

CURR_DIR = Path(__file__).resolve().parent # commands/
load_dotenv(CURR_DIR / '.env')

bearer_token = os.environ.get("BEARER_TOKEN")
mangastylebot_id = os.environ.get("MANGASTYLEBOT_ID")

def bearer_oauth(r):
    r.headers["Authorization"] = "Bearer {}".format(bearer_token)
    return r

def get_request(url):
    response = requests.get(url, auth=bearer_oauth)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        reset_time = int(response.headers["x-rate-limit-reset"])
        sleep_time = reset_time - int(time.time()) + 1
        if sleep_time > 0:
            log.warning(
                "Rate limit exceeded. "
                f"Sleeping for {sleep_time} seconds."
            )
            time.sleep(sleep_time)
        return get_request(url)
    else:
        raise ValueError("API call did not succeed, http response: {}".format(response.json()))

def create_get_following_url(user_id, next_token=None):
    url = ("https://api.twitter.com/2/users/{}/following"
           "?max_results=1000"
           "&user.fields=id,profile_image_url,public_metrics,username"
           .format(user_id))
    if next_token:
        url += "&pagination_token={}".format(next_token)
    return url

def get_who_user_is_following(user_id):  
    url = create_get_following_url(user_id)
    json_resp = get_request(url)
    
    total_json = json_resp['data']
    next_token = json_resp['meta'].get('next_token', None)
    while next_token:
        url = create_get_following_url(user_id, next_token=next_token)
        json_resp = get_request(url)
        total_json += json_resp['data']
        next_token = json_resp['meta'].get('next_token', None)
    
    return total_json

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

def save_artist_data(user_data):
    try:
        artist, created = TwitterArtist.objects.update_or_create(
            user_id=user_data['id'],
            defaults={
                'username': user_data['username'],
                'name': user_data['name'],
                'followers_count': user_data['public_metrics']['followers_count'],
                'profile_image_url': user_data['profile_image_url'],
            }
        )
        return artist
    except Exception as e:
        raise CommandError('Something went wrong at user {}: {}'.format(user_data['username'], e))

def save_tweet_data(tweet_data, artist):
    try:
        created_at = make_aware(dt.strptime(tweet_data['created_at'], dt_fmt))
        tweet, created = MediaTweet.objects.update_or_create(
            tweet_id=tweet_data['id'],
            defaults={
                'text': tweet_data['text'],
                'likes_count': tweet_data['public_metrics']['like_count'],
                'retweets_count': tweet_data['public_metrics']['retweet_count'],
                'created_at': created_at,
                'lang': tweet_data['lang'],
                'possibly_sensitive': tweet_data['possibly_sensitive'],
                'author': artist,
            }
        )
        return tweet
    except Exception as e:
        raise CommandError('Something went wrong for tweet {}: {}'.format(tweet_data['id'], e))

def save_media_data(media_data, tweet):
    try:
        media = MediaAttachment.objects.update_or_create(
            media_id=media_data['media_key'],
            defaults={
                'media_url': media_data['url'],
                'media_type': media_data['type'],
                'media_style': '',
                'parent_tweet': tweet,
            }
        )
        return media
    except Exception as e:
        raise CommandError('Something went wrong for media {}: {}'.format(media_data['url'], e))

def update_artist_tweet_media(username):
    try:
        # 1. Send request to twitter api
        json_response = get_recent_media_tweets(username)
        result_count = json_response['meta']['result_count']

        # 2. If no recent tweets, call save and return 0
        if result_count == 0:
            artist = TwitterArtist.objects.get(username=username)
            artist.save()
            return result_count

        # 3. If recent tweets, update artist data
        artist = save_artist_data(json_response['includes']['users'][0])

        # 4. Map media key to media data like url, type
        media_id_map = {media_dict['media_key']: media_dict 
                        for media_dict in json_response['includes']['media']}

        # 5. Save each tweet and its attached media
        for tweet_data in json_response['data']:
            tweet = save_tweet_data(tweet_data, artist)

            media_ids = tweet_data['attachments']['media_keys']
            for media_id in media_ids:
                media_data = media_id_map[media_id]
                save_media_data(media_data, tweet)
        
        # 6. Return number of tweets saved
        return result_count
    except ValueError as ve:
        raise CommandError("Error {} for artist {}.".format(ve, username))