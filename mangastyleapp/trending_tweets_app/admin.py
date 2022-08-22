from django.contrib import admin

from .models import TwitterArtist, MediaTweet, MediaAttachment

class MediaAttachmentInline(admin.TabularInline):
    model = MediaAttachment
    extra = 1

class MediaTweetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at',)
    inlines = [MediaAttachmentInline]
    search_fields = ['author__username']

class MediaTweetInline(admin.TabularInline):
    model = MediaTweet
    extra = 1

class TwitterArtistAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_id', 'followers_count', 'profile_image_url')
    readonly_fields = ('last_updated',)
    inlines = [MediaTweetInline]
    search_fields = ['username']

admin.site.register(TwitterArtist, TwitterArtistAdmin)
admin.site.register(MediaTweet, MediaTweetAdmin)
admin.site.register(MediaAttachment)