from django.contrib import admin
from django.urls import path
from .models import TwitterArtist, MediaTweet, MediaAttachment
from django.http import HttpResponse

admin.site.site_header = "Mangastyle Admin Dashboard"

class TwitterArtistAdmin(admin.ModelAdmin):
    fields = ('last_updated', 'username', 'followers_count', 'user_id', 'name', 'profile_image_url')
    list_display = ('username', 'followers_count', 'last_updated')

class MediaTweetAdmin(admin.ModelAdmin):
    fields = ('author', 'created_at', 'likes_count', 'retweets_count', 'possibly_sensitive', 'tweet_id', 'text', 'lang')
    list_display = ('author', 'likes_count', 'created_at')

class MediaAttachmentAdmin(admin.ModelAdmin):
    fields = ('style', 'training_data', 'media_url', 'parent_tweet', 'media_id', 'media_type')
    list_display = ('parent_tweet', 'style', 'training_data')

admin.site.register(TwitterArtist, TwitterArtistAdmin)
admin.site.register(MediaTweet, MediaTweetAdmin)
admin.site.register(MediaAttachment, MediaAttachmentAdmin)