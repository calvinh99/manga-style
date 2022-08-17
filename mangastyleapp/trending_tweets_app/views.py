from django.shortcuts import render

from .models import TwitterArtist, MediaTweet, MediaAttachment

# Create your views here.
def index(request):
    return render(request, 'trending_tweets_app/index.html')