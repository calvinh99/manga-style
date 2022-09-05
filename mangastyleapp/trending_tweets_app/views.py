from tempfile import TemporaryFile
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.timezone import now
from datetime import timedelta

from django.db.models import Q
from .models import MediaTweet


import logging
logger = logging.getLogger(__name__)

tweets_per_page = 50

def abbreviation_to_num(abb):
    abbreviations = {
        '1K': 1000,
        '10K': 10000,
        '100K': 100000,
        '1M': 1000000,
    }
    return abbreviations.get(abb, 0)

def style_str_to_class_id(style_str):
    style_classes = {
        'MangaColor': 0,
        'MangaInk': 1,
        'Sketch': 2,
        'Fusion': 3,
        'Hentai': 4,
    }
    return style_classes.get(style_str, -1)

def tweets(request):
    logging.debug("HttpRequest GET dict: {request.GET}")

    page_num = 1
    if request.GET.get('page'):
        try:
            page_num = int(request.GET.get('page'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")

    # Query String Filters
    # TODO: Currently the below filter will also get rid of tweets that have 
    #       multiple media attachments where even one is not art.
    tweets_query = MediaTweet.objects.filter(~Q(mediaattachment__style=9999))

    days = 1
    if request.GET.get('days'):
        try:
            days = int(request.GET.get('days'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")
    time_filter = now() - timedelta(days=days)
    tweets_query = tweets_query.filter(created_at__gte=time_filter)

    if request.GET.get('minfollowers'):
        try:
            minfollowers = abbreviation_to_num(request.GET.get('minfollowers'))
            tweets_query = tweets_query.filter(author__followers_count__gte=minfollowers)
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")
    
    if request.GET.get('maxfollowers'):
        try:
            if request.GET.get('maxfollowers') != 'None':
                maxfollowers = abbreviation_to_num(request.GET.get('maxfollowers'))
                tweets_query = tweets_query.filter(author__followers_count__lte=maxfollowers)
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")
    
    if request.GET.get('minlikes'):
        try:
            minlikes = abbreviation_to_num(request.GET.get('minlikes'))
            tweets_query = tweets_query.filter(likes_count__gte=minlikes)
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")
    
    if request.GET.get('style'):
        try:
            style = style_str_to_class_id(request.GET.get('style'))
            if style != -1:
                tweets_query = tweets_query.filter(mediaattachment__style=style)
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")

    tweets_query = tweets_query.order_by('-likes_count')
    tweet_paginator = Paginator(tweets_query.all(), tweets_per_page)

    rank_inc = (page_num - 1) * tweets_per_page

    context = {
        'trending_tweets': tweet_paginator.get_page(page_num),
        'rank_increment': rank_inc, # Take page number as arg to this fn
        'num_pages': tweet_paginator.num_pages,
        'current_page': page_num,
    }
    return render(request, 'trending_tweets_app/index.html', context=context)
