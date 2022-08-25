import os
import time

import requests

from pathlib import Path
from dotenv import load_dotenv

from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment
from django.core.management.base import CommandError

CURR_DIR = Path(__file__).resolve().parent # commands/
load_dotenv(CURR_DIR / '.env')

bearer_token = os.environ.get("BEARER_TOKEN")
mangastylebot_id = os.environ.get("MANGASTYLEBOT_ID")

def create_get_following_url(user_id, next_token=None):
    url = ("https://api.twitter.com/2/users/{}/following"
           "?max_results=1000"
           "&user.fields=id,profile_image_url,public_metrics,username"
           .format(user_id))
    if next_token:
        url += "&pagination_token={}".format(next_token)
    return url

def bearer_oauth(r):
    r.headers["Authorization"] = "Bearer {}".format(bearer_token)
    return r

def get_request(url):
    response = requests.get(url, auth=bearer_oauth)
    if response.status_code != 200:
        raise ValueError("API call did not succeed, http response: {}".format(response.json()))
    return response.json()

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
    except Exception as e:
        raise CommandError('Something went wrong at user {}: {}'.format(user_data['username'], e))
    return artist