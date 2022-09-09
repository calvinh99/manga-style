import os
import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from trending_tweets_app.models import MediaAttachment

import logging
log = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Save media attachments with field training_data=True to a csv file."

    def handle(self, *args, **options):
        save_path = Path('/Users/calvinhuang/ml/mangastyle/data/twitter/twitter_images.csv')
        header = ['media_id', 'media_url', 'style']
        rows = []

        training_data = MediaAttachment.objects.filter(training_data=True).all()
        for media in training_data:
            row = [media.media_id, media.media_url, media.style]
            rows.append(row)

        with open(save_path.resolve(), 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
            self.stdout.write(self.style.SUCCESS(f"Saved {len(rows)} images to {save_path}"))

