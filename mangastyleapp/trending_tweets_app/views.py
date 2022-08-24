from django.shortcuts import render

from .models import TwitterArtist, MediaTweet, MediaAttachment

# Create your views here.
def index(request):
    page_num = 0
    rank_inc = page_num * 25
    context = {
        'top_25_trending_media_tweets': MediaTweet.objects.order_by('-likes_count')[:100],
        'rank_increment': rank_inc, # Take page number as arg to this fn
    }
    return render(request, 'trending_tweets_app/index.html', context=context)