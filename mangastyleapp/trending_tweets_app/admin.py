from django.contrib import admin
from django.urls import path
from .models import TwitterArtist, MediaTweet, MediaAttachment
from django.http import HttpResponse
from django.utils.html import format_html

import logging
log = logging.getLogger(__name__)

admin.site.site_header = "Mangastyle Admin Dashboard"

class MediaTweetInline(admin.TabularInline):
    model = MediaTweet
    extra = 0

class MediaAttachmentInline(admin.TabularInline):
    model = MediaAttachment
    readonly_fields = ('display_media',)
    fields = ('style', 'training_data', readonly_fields)
    extra = 0

    @admin.display(description='Image')
    def display_media(self, obj):
        return format_html(f"<img style='width: 500px;' src='{obj.media_url}'>")

class TwitterArtistAdmin(admin.ModelAdmin):
    search_fields = ['username']
    inlines = [MediaTweetInline]
    fields = ('last_updated', 'username', 'followers_count', 'user_id', 'name', 'profile_image_url')
    list_display = ('username', 'followers_count', 'last_updated', 'get_num_tweets')

class MediaTweetAdmin(admin.ModelAdmin):
    search_fields = ['author__username']
    list_filter = ['mediaattachment__training_data', 'mediaattachment__style']
    inlines = [MediaAttachmentInline]
    raw_id_fields = ('author',)
    fields = ('author', 'created_at', 'likes_count', 'retweets_count', 'possibly_sensitive', 'tweet_id', 'text', 'lang')
    list_display = ('author', 'likes_count', 'created_at')

class MediaAttachmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('parent_tweet',)
    readonly_fields = ('display_media',)
    fields = ('style', 'training_data', readonly_fields, 'media_url', 'parent_tweet', 'media_id', 'media_type')
    list_display = ('parent_tweet', 'style', 'training_data')

    @admin.display(description='Image')
    def display_media(self, obj):
        return format_html(f"<img style='height: 200px;' src='{obj.media_url}'>")

admin.site.register(TwitterArtist, TwitterArtistAdmin)
admin.site.register(MediaTweet, MediaTweetAdmin)
admin.site.register(MediaAttachment, MediaAttachmentAdmin)