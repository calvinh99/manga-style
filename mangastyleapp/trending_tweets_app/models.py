from django.db import models
from django.utils import timezone

import datetime

class TwitterArtist(models.Model):
    user_id = models.CharField(max_length=40, unique=True, blank=False)
    username = models.CharField(max_length=15, unique=True, blank=False)
    name = models.CharField(max_length=50, unique=False, default='', blank=True)
    followers_count = models.IntegerField(default=0)
    profile_image_url = models.URLField(max_length=200, default='', blank=True)
    last_updated = models.DateTimeField(blank=False)
    
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """Override save method to init last_updated field to datetime.min upon creation."""
        if not self.pk:
            self.last_updated = datetime.datetime.min
        else:
            self.last_updated = timezone.now()
        super(TwitterArtist, self).save(*args, **kwargs)

class MediaTweet(models.Model):
    tweet_id = models.CharField(max_length=40, unique=True, blank=False)
    text = models.URLField(max_length=560, unique=False, default='', blank=True)
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=False)
    lang = models.CharField(max_length=5, default='', blank=True)
    possibly_sensitive = models.BooleanField(default=False, blank=True)
    author = models.ForeignKey(TwitterArtist, to_field='user_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.author.username + " tweeted at " + self.created_at.strftime("%Y-%m-%d")

class MediaAttachment(models.Model):
    media_id = models.CharField(max_length=40, unique=True, blank=False)
    media_url = models.URLField(max_length=200, unique=True, blank=False)
    media_type = models.CharField(max_length=10)
    media_style = models.CharField(max_length=10, default='')
    parent_tweet = models.ForeignKey(MediaTweet, to_field='tweet_id', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.parent_tweet.author.username + " " + self.media_url