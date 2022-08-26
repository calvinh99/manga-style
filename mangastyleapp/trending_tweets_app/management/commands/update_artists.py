from django.core.management.base import BaseCommand, CommandError
from trending_tweets_app.models import TwitterArtist

import time
from . import twitter_api

class Command(BaseCommand):
    help = "Update twitter artists followed by mangastylebot in database."

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--add',
            action='store_true',
            help='Add newly followed artists.',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete artists that are no longer followed.',
        )

    def print_flush(self, text, ending='\n'):
        self.stdout.write(text, ending=ending)
        self.stdout.flush()
        time.sleep(0.01)

    def log_add(self, user_data):
        if TwitterArtist.objects.filter(user_id=user_data['id']).exists():
            return 0
        else:
            self.print_flush("Adding artist {}".format(user_data['username']), ending=' ... ')
            try:
                twitter_api.save_artist_data(user_data)
                self.print_flush(self.style.SUCCESS("Added artist {}.".format(user_data['username'])))
                return 1
            except Exception as e:
                self.print_flush(self.style.ERROR("Error adding artist {}: {}".format(user_data['username'], e)))
                return 0
    
    def log_delete(self, artist):
        self.print_flush("Deleting artist {}".format(artist.username), ending=' ... ')
        try:
            deleted_objects = artist.delete()
            self.print_flush(self.style.SUCCESS("Deleted {} objects: {}"
                                                .format(deleted_objects[0], deleted_objects[1])))
            return 1
        except Exception as e:
            self.print_flush(self.style.ERROR("Error deleting artist {}: {}".format(artist.username, e)))
            return 0

    def handle(self, *args, **options):
        following_data = twitter_api.get_who_user_is_following(twitter_api.mangastylebot_id)

        if options['add']:
            n_added = 0
            for user_data in following_data:
                n_added += self.log_add(user_data)
            self.print_flush(self.style.SUCCESS(f'Successfully added {n_added} twitter artists.'))

        if options['delete']:
            following_ids = set(user_data['id'] for user_data in following_data)

            n_deleted = 0
            for artist in TwitterArtist.objects.all():
                if artist.user_id not in following_ids:
                    n_deleted += self.log_delete(artist)
            self.print_flush(self.style.SUCCESS(f'Successfully deleted {n_deleted} twitter artists.'))