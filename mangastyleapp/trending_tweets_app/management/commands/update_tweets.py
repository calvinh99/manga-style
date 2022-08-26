import time

from django.core.management.base import BaseCommand, CommandError
from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment

from datetime import datetime as dt
from django.utils.timezone import make_aware

from . import twitter_api

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
    
    def log_update(self, username):
        self.print_flush("Updating artist {}".format(username), ending=' ... ')
        try:
            result_count = twitter_api.update_artist_tweet_media(username)
            self.print_flush(self.style.SUCCESS("Updated artist {} with {} tweets."
                                                .format(username, result_count)))
            return 1
        except Exception as e:
            self.print_flush(self.style.ERROR("Error updating artist {}: {}".format(username, e)))
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
            for artist in TwitterArtist.objects.all().order_by('last_updated'):
                if artist.last_updated > dt_checkpoint: # if more recent
                    self.print_flush(self.style.WARNING(f"Finished updating artists up till checkpoint: {dt_checkpoint}."))
                    break
                n_updated += self.log_update(artist.username)

            self.print_flush(self.style.SUCCESS(f"Updated {n_updated}/{TwitterArtist.objects.count()} artists."))
        else:
            for username in options['usernames']:
                self.log_update(username)