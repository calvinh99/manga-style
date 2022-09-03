from django.contrib import admin

from .models import TwitterArtist, MediaTweet, MediaAttachment

class MediaAttachmentAdmin(admin.ModelAdmin):
    list_display = ('parent_tweet', 'style')
    search_fields = ['style']

class MediaAttachmentInline(admin.TabularInline):
    model = MediaAttachment
    extra = 1

class MediaTweetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at' ,'likes_count', 'possibly_sensitive')
    inlines = [MediaAttachmentInline]
    search_fields = ['author__username']
    list_filter = ('possibly_sensitive',)

class MediaTweetInline(admin.TabularInline):
    model = MediaTweet
    extra = 1

class TwitterArtistAdmin(admin.ModelAdmin):
    list_display = ('username', 'followers_count', 'last_updated')
    readonly_fields = ('last_updated',)
    inlines = [MediaTweetInline]
    search_fields = ['username']

admin.site.register(TwitterArtist, TwitterArtistAdmin)
admin.site.register(MediaTweet, MediaTweetAdmin)
admin.site.register(MediaAttachment, MediaAttachmentAdmin)