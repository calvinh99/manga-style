import time

from django.core.management.base import BaseCommand, CommandError
from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment

from datetime import datetime as dt
from django.utils.timezone import make_aware

from . import twitter_api

import logging
log = logging.getLogger(__name__)

dt_checkpoint_path = twitter_api.CURR_DIR / 'dt_checkpoint.txt'

def save_dt_checkpoint(dt_checkpoint):
    with open(dt_checkpoint_path, 'w') as f:
        dt_str = dt_checkpoint.strftime(twitter_api.dt_fmt)
        f.write(dt_str)
        return dt_str

def load_dt_checkpoint():
    with open(dt_checkpoint_path, 'r') as f:
        dt_checkpoint = make_aware(dt.strptime(f.read(), twitter_api.dt_fmt))
    return dt_checkpoint

class Command(BaseCommand):
    help = "Update the user data, recent tweets, and media attachments of all saved twitter artists."

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)
        parser.add_argument(
            '--finish',
            action='store_true',
            help='Update all artists up till checkpoint (only use if full update was interrupted).',
        )
    
    def print_flush(self, text, ending='\n'):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()
        time.sleep(0.01)
        
    def log_update(self, usernames):
        self.print_flush("Updating group of users", ending=' ... \n')
        try:
            # 1. Get json response
            json_response = twitter_api.get_recent_media_tweets(usernames)
            
            # 2. If no results, warn and save
            if json_response['meta']['result_count'] == 0:
                self.print_flush(self.style.WARNING(f"None of users: {usernames} posted in the past 7 days!"))
                for artist in TwitterArtist.objects.filter(username__in=usernames):
                    artist.save()
                return 0
            
            # 2. Create mappings for fast search
            map_username_to_data = {user_data['username']:user_data
                                    for user_data in json_response['includes']['users']}
            
            map_author_id_to_tweets = dict()
            for tweet_data in json_response['data']:
                map_author_id_to_tweets.setdefault(tweet_data['author_id'],[]).append(tweet_data)
            
            map_media_key_to_data = {media_data['media_key']: media_data 
                                     for media_data in json_response['includes']['media']}
            
            del json_response # don't need this anymore

            # 3. For each user
            n_updated = 0
            for username in usernames:
                self.print_flush(f"    Updating {username}...", ending=' ... ')
                try:
                    tweets_updated = 0
                    
                    if user_data := map_username_to_data.get(username): # := requires Python 3.8 or later
                        artist = twitter_api.save_artist_data(user_data)

                        # 4. For each tweet
                        if tweets := map_author_id_to_tweets.get(artist.user_id):
                            for tweet_data in tweets:
                                tweet = twitter_api.save_tweet_data(tweet_data, artist)

                                # 5. For each media attachment
                                media_keys = tweet_data['attachments']['media_keys']
                                for media_key in media_keys:
                                    media_data = map_media_key_to_data[media_key]
                                    twitter_api.save_media_data(media_data, tweet)
                                
                                tweets_updated += 1
                    else: # if no new tweets from user, call save() to update last_updated
                        artist = TwitterArtist.objects.get(username=username)
                        artist.save()
                    self.print_flush(self.style.SUCCESS(f"Updated artist {username} with ")
                                     + self.style.MIGRATE_HEADING(f"{tweets_updated}")
                                     + self.style.SUCCESS(" tweets."))
                    n_updated += 1
                except Exception as e:
                    self.print_flush(self.style.ERROR(f"Error updating {username}: {e}"))
            
            return n_updated
        except Exception as e:
            self.print_flush(self.style.ERROR(f"Error updating group: {usernames}"))
            return 0

    def handle(self, *args, **options):
        if options['usernames'][0] == 'all':
            if not options['finish']:
                # Save most recently updated to checkpoint
                dt_checkpoint = TwitterArtist.objects.order_by('-last_updated')[0].last_updated
                dt_str = save_dt_checkpoint(dt_checkpoint)
                self.print_flush(self.style.SUCCESS("Saved dt checkpoint: {}".format(dt_str)))
            else:
                # Load checkpoint
                dt_checkpoint = load_dt_checkpoint()

            self.print_flush("Updating all artists", ending='\n{}\n'.format('-'*40))

            n_updated = 0
            query_usernames = []
            for artist in TwitterArtist.objects.all().order_by('last_updated'):
                query_usernames.append(artist.username)

                # If reached end, update artists in query_usernames
                if artist.last_updated >= dt_checkpoint:
                    n_updated += self.log_update(query_usernames)
                    self.print_flush(self.style.WARNING(f"Finished updating artists up till checkpoint: {dt_checkpoint}."))
                    break

                # Update when query reaches just under 512 characters (Twitter API limit)
                if len(query_usernames) >= 19:
                    query = twitter_api.create_search_query(query_usernames)
                    if twitter_api.get_query_length(query) + 24 > 512: # can't add any more users
                        n_updated += self.log_update(query_usernames)
                        query_usernames.clear()

            self.print_flush(self.style.SUCCESS(f"Updated {n_updated}/{TwitterArtist.objects.count()} artists."))
        else:
            self.log_update(options['usernames'])