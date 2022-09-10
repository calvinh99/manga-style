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

from mangastyleapp.settings import BASE_DIR

# logging
import logging

log = logging.getLogger(__name__)

dt_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

CURR_DIR = Path(__file__).resolve().parent # commands/
load_dotenv(BASE_DIR / '.env')

bearer_token = os.environ.get("BEARER_TOKEN")
mangastylebot_id = os.environ.get("MANGASTYLEBOT_ID")

def bearer_oauth(r):
    r.headers["Authorization"] = "Bearer {}".format(bearer_token)
    return r

def get_request(url):
    response = requests.get(url, auth=bearer_oauth)
    log.warning(f"Remaining Requests: {response.headers.get('x-rate-limit-remaining')}")
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
    elif response.status_code == 503:
        log.warning("Service Unavailable. Sleeping for 3 seconds.")
        time.sleep(3)
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

def create_search_query(usernames: list):
    query = f"(from%3A{usernames[0]}" # `%3A` is url encoding for `:` and `%20` is ` `    
    for username in usernames[1:]:
        query += f"%20OR%20from%3A{username}" # ` OR from:{username}`
    query += ")%20-is%3Aretweet%20-is%3Areply%20-is%3Aquote%20has%3Aimages"
    
    return query

def get_query_length(query):
    return len(query) - query.count('%')*2 # url encodings only count for 1 char

def create_get_search_url(usernames, next_token=None):
    url = ("https://api.twitter.com/2/tweets/search/recent"
           f"?query={create_search_query(usernames)}"
           "&max_results=100"
           "&sort_order=recency"
           "&tweet.fields=id,text,public_metrics,created_at,lang,attachments,possibly_sensitive"
           "&expansions=attachments.media_keys,author_id"
           "&media.fields=media_key,type,url"
           "&user.fields=id,profile_image_url,public_metrics,username")
    if next_token:
        url += "&pagination_token={}".format(next_token)
    return url

def get_recent_media_tweets(usernames):
    # 1. Get initial response
    url = create_get_search_url(usernames)
    json_resp = get_request(url)
    
    # 2. Initialize total
    total_json = json_resp.copy()
    
    # 3. Iterate for each page and add its data to total
    next_token = json_resp['meta'].get('next_token', None)
    while next_token:
        url = create_get_search_url(usernames, next_token=next_token)
        json_resp = get_request(url)
        total_json['data'] += json_resp['data']
        total_json['includes']['media'] += json_resp['includes']['media']
        total_json['includes']['users'] += json_resp['includes']['users']
        next_token = json_resp['meta'].get('next_token', None)
    
    return total_json

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
                'parent_tweet': tweet,
                'training_data': False,
            }
        )
        return media
    except Exception as e:
        raise CommandError('Something went wrong for media {}: {}'.format(media_data['url'], e))