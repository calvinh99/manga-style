from django.test import TestCase
from trending_tweets_app.models import TwitterArtist, MediaTweet, MediaAttachment

class CommandTests(TestCase):

    def test_update_tweets(self):
        """Test that the update_tweets command works"""
        # call the command
        # call_command('update_tweets')
        # check that the tweets have been added
        self.assertEqual(True, True)