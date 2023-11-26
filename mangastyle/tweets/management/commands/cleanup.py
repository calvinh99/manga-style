import requests
from django.core.management.base import BaseCommand
from mangastyle.tweets.models import MediaAttachment, MediaTweet

class Command(BaseCommand):
    help = 'Delete MediaTweets with broken image URLs in MediaAttachments'

    def __init__(self):
        super().__init__()
        self.processed_file = 'processed_tweets.txt'

    def check_url(self, url):
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        return False

    def last_processed_id(self):
        try:
            with open(self.processed_file, 'r') as file:
                last_line = file.readlines()[-1]
                return int(last_line.strip())
        except (FileNotFoundError, IndexError, ValueError):
            return None

    def handle(self, *args, **kwargs):
        last_id = self.last_processed_id()
        query_set = MediaAttachment.objects.all()
        if last_id is not None:
            query_set = query_set.filter(id__gt=last_id)

        for attachment in query_set:
            if not self.check_url(attachment.media_url):
                try:
                    tweet_to_delete = attachment.parent_tweet
                    tweet_to_delete.delete()
                    self.stdout.write(self.style.SUCCESS(f'Deleted MediaTweet {tweet_to_delete} with broken URL: {attachment.media_url}'))
                except MediaTweet.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Skipping deletion. MediaTweet for {attachment.media_url} does not exist.'))
            else:
                with open(self.processed_file, 'a') as file:
                    file.write(f'{attachment.id}\n')
