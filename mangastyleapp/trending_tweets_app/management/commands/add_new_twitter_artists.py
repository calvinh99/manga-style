from django.core.management.base import BaseCommand, CommandError
from trending_tweets_app.models import TwitterArtist

import os
from pathlib import Path
from dotenv import load_dotenv

import time
import requests

APP_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(APP_DIR / '.env')

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

def save_artist_data(user_data, update_existing=False):
    try:
        artist = TwitterArtist.objects.get(user_id=user_data['id'])
        if update_existing:
            artist.name = ''     # TODO: test out MySQL utf8mb4 for multi-language and emojis
            artist.username = user_data['username']
            artist.followers_count = user_data['public_metrics']['followers_count']
            artist.profile_image_url = user_data['profile_image_url']
            artist.save()
    except TwitterArtist.DoesNotExist:
        artist = TwitterArtist(user_id=user_data['id'], 
                               username=user_data['username'], 
                               name='',     # TODO: test out MySQL utf8mb4 for multi-language and emojis
                               followers_count=user_data['public_metrics']['followers_count'], 
                               profile_image_url=user_data['profile_image_url'])
        artist.save()
    except Exception as e:
        raise CommandError('Something went wrong at user {}: {}'.format(user_data['username'], e))
    return artist

class Command(BaseCommand):
    help = "Fetch all data of users that mangastylebot is following using Twitter API."

    def log_add(self, user_data):
        try:
            artist = TwitterArtist.objects.get(user_id=user_data['id'])
            return 0
        except TwitterArtist.DoesNotExist:
            self.stdout.write("Adding artist {}".format(user_data['username']), ending=' ... ')
            self.stdout.flush()
            time.sleep(0.01)

            try:
                save_artist_data(user_data)
                self.stdout.write(self.style.SUCCESS("Added artist {}.".format(user_data['username'])))
                self.stdout.flush()
                time.sleep(0.01)
                return 1
            except Exception as e:
                self.stdout.write(self.style.ERROR("Error adding artist {}: {}".format(user_data['username'], e)))
                self.stdout.flush()
                time.sleep(0.01)
                return 0

    def handle(self, *args, **options):
        following_data = get_who_user_is_following(mangastylebot_id)

        n_added = 0
        for user_data in following_data:
            n_added += self.log_add(user_data)
        self.stdout.write(self.style.SUCCESS('Successfully added {} twitter artists.'.format(n_added)))