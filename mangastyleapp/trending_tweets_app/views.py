from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.timezone import now
from datetime import timedelta

from .models import MediaTweet

import logging
logger = logging.getLogger(__name__)

tweets_per_page = 50

def tweets(request):
    logging.debug("HttpRequest GET dict: {request.GET}")

    page_num = 1
    if request.GET.get('page'):
        try:
            page_num = int(request.GET.get('page'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")

    days = 7
    if request.GET.get('days'):
        try:
            days = int(request.GET.get('days'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")
    time_filter = now() - timedelta(days=days)

    media_tweets = MediaTweet.objects.filter(created_at__gt=time_filter).order_by('-likes_count').all()
    tweet_paginator = Paginator(media_tweets, tweets_per_page)

    rank_inc = (page_num - 1) * tweets_per_page

    context = {
        'trending_tweets': tweet_paginator.get_page(page_num),
        'rank_increment': rank_inc, # Take page number as arg to this fn
        'num_pages': tweet_paginator.num_pages,
        'current_page': page_num,
    }
    return render(request, 'trending_tweets_app/index.html', context=context)
