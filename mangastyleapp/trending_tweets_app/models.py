import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone

class TwitterArtist(models.Model):
    user_id = models.CharField(max_length=40, unique=True, blank=False)
    username = models.CharField(max_length=15, unique=True, blank=False)
    followers_count = models.IntegerField(default=0)
    profile_image_url = models.URLField(max_length=200, default='', blank=True)
    
    def __str__(self):
        return self.username

    def get_recent_media_tweets(self):
        """
        Gets recent media tweets (at max 7 days ago) using
        twitter recent search API request. Store returned 
        tweets and save to database.

        Get created_at of most recent MediaTweet. If older 
        than one week, then set start_time to one week ago, 
        otherwise, set start_time to most recent MediaTweet's
        created_at datetime.
        """
        print("Yet to be Implemented")

class MediaTweet(models.Model):
    tweet_id = models.CharField(max_length=40, unique=True, blank=False)
    tweet_url = models.URLField(max_length=200, unique=True, blank=False)
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=False)
    lang = models.CharField(max_length=5, default='', blank=True)
    author = models.ForeignKey(TwitterArtist, to_field='user_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.tweet_url

    def get_media_urls(self):
        """
        Gets media urls from Media objects in one-to-many relation.
        """
        print("Yet to be Implemented")

class MediaAttachment(models.Model):
    media_id = models.CharField(max_length=40, unique=True, blank=False)
    media_url = models.URLField(max_length=200, unique=True, blank=False)
    media_type = models.CharField(max_length=10)
    # perhaps a field for class like 'media_style' after implementing our ML model
    parent_tweet = models.ForeignKey(MediaTweet, to_field='tweet_id',on_delete=models.CASCADE)
    
    def __str__(self):
        return self.media_url

    def get_style_classified(self):
        """
        Calls our ML Model microservice to classify as 'mangastyle', 
        'fudastyle', 'nsfw', etc.
        """
        print("Yet to be Implemented")