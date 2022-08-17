from django.contrib import admin

from .models import TwitterArtist, MediaTweet, MediaAttachment

class MediaTweetInline(admin.TabularInline):
    model = MediaTweet
    extra = 1

class TwitterArtistAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_id', 'followers_count', 'profile_image_url')
    inlines = [MediaTweetInline]
    list_filter = ['followers_count']
    search_fields = ['username']

admin.site.register(TwitterArtist, TwitterArtistAdmin)
admin.site.register(MediaTweet)
admin.site.register(MediaAttachment)