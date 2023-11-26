import datetime
from django.utils import timezone

from django.test import TestCase
from tweets.models import TwitterArtist, MediaTweet, MediaAttachment

class TwitterArtistModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = TwitterArtist.objects.create(
            user_id='1234567890',
            username='test_artist',
            name='Test Artist',
            followers_count=100,
            profile_image_url='https://pbs.twimg.com/profile_images/1234567890/test_artist.jpg',
            last_updated=timezone.now(),
            hide=False
        )
    
    def test_user_id_label(self):
        max_length = self.artist._meta.get_field('user_id').max_length
        self.assertEqual(max_length, 40)

    # although created with timezone.now(), last_updated should be saved as datetime.datetime.min
    def test_last_updated_init(self):
        self.assertEqual(self.artist.last_updated, datetime.datetime.min)

    # after saving, last updated should be updated to current time
    def test_last_updated_save(self):
        time_before_save = timezone.now()
        self.artist.save()
        self.assertTrue(time_before_save <= self.artist.last_updated <= timezone.now())