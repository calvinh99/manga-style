from tempfile import TemporaryFile
from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import Http404
from django.utils.timezone import now
from datetime import timedelta

from django.db.models import Q, Avg
from .models import MediaTweet

import json

import logging
log = logging.getLogger(__name__)

# filters is a single place to control the frontend and backend for applying filters
filters = {
    'days': {
        'filterTitle': 'Only option is All Time due to Twitter API stoppage.',
        'filterValues': {
            'All Time': None,
        },
        'radioName': 'days',
        'radioDirection': 'row',
        'radioToCheck': 'All Time',
        'default': None,
    },
    'minfollowers': {
        'filterTitle': 'Minimum user followers',
        'filterValues': {
            'None': None,
            '1K': 1000,
            '10K': 10000,
            '100K': 100000,
            '500K': 500000,
            '1M': 1000000,
        },
        'radioName': 'minfollowers',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'maxfollowers': {
        'filterTitle': 'Maximum user followers',
        'filterValues': {
            '1K': 1000,
            '10K': 10000,
            '100K': 100000,
            '500K': 500000,
            '1M': 1000000,
            'None': None,
        },
        'radioName': 'maxfollowers',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'minlikes': {
        'filterTitle': 'Minimum likes',
        'filterValues': {
            'Default': 0,
            '10K': 10000,
            '50K': 50000,
            '100K': 100000,
            '200K': 200000,
        },
        'radioName': 'minlikes',
        'radioDirection': 'row',
        'radioToCheck': 'Default',
        'default': 0,
    },
    'maxlikes': {
        'filterTitle': 'Maximum likes',
        'filterValues': {
            '10K': 10000,
            '50K': 50000,
            '100K': 100000,
            '200K': 200000,
            'None': None,
        },
        'radioName': 'maxlikes',
        'radioDirection': 'row',
        'radioToCheck': 'None',
        'default': None,
    },
    'style': {
        'filterTitle': 'NSFW Filter',
        'filterValues': {
            'mangastyle': 0,
            'nsfw': 1,
        },
        'radioName': 'style',
        'radioDirection': 'column',
        'radioToCheck': 'mangastyle',
        'default': 0,
    },
}

# return the query str's value if it exists and is valid, else return the default
def get_filter_query_value(request, filter_name):
    query_value = filters[filter_name]['default']
    if query_str := request.GET.get(filter_name): # from the url, so the Javascript handles this
        query_value = filters[filter_name]['filterValues'].get(query_str, query_value)
    return query_value

# requires python > 3.8
def create_filtered_query_set(request):
    # Remove all tweets classified as 'Not Art' (keep unlabeled tweets though)
    tweets_query = (MediaTweet.objects
                    .filter(author__hide=False)) # manual limiting of certain twitter artists

    # 1. Days Filter - deprecated due to Twitter API stoppage
    # days = get_filter_query_value(request, 'days')
    # if days is not None:
    #     time_filter = now() - timedelta(days=days)
    #     tweets_query = tweets_query.filter(created_at__gte=time_filter)

    # 2. Min Followers Filter
    min_followers = get_filter_query_value(request, 'minfollowers')
    if min_followers:
        tweets_query = tweets_query.filter(author__followers_count__gte=min_followers)

    # 3. Max Followers Filter
    max_followers = get_filter_query_value(request, 'maxfollowers')
    if max_followers:
        tweets_query = tweets_query.filter(author__followers_count__lte=max_followers)

    # 4. Min Likes Filter
    min_likes = get_filter_query_value(request, 'minlikes')
    if min_likes:
        min_likes = max(min_likes, 0)
        tweets_query = tweets_query.filter(likes_count__gte=min_likes)

    # 5. Max Likes Filter
    max_likes = get_filter_query_value(request, 'maxlikes')
    if max_likes:
        tweets_query = tweets_query.filter(likes_count__lte=max_likes)

    # 6. Style Filter
    style = get_filter_query_value(request, 'style')
    if style == 0:
        tweets_query = tweets_query.filter(possibly_sensitive=False)
    elif style == 1:
        tweets_query = tweets_query.filter(possibly_sensitive=True)
    
    # 7. Sort by likes descending
    tweets_query = tweets_query.order_by('-likes_count')
    log.warning(f"QUERY: {tweets_query.query}")
    return tweets_query

def tweets(request):
    # Set our page number
    page_num = 1
    if request.GET.get('page'):
        try:
            page_num = int(request.GET.get('page'))
        except Exception as e:
            logging.debug(f"HttpRequest {request} resulted in Exception: {e}")
            raise Http404("Page not found")

    # Parameters
    tweets_per_page = 50
    rank_inc = (page_num - 1) * tweets_per_page # Aesthetic just to determine the tweet ranking

    tweets_query = create_filtered_query_set(request)
    tweet_paginator = Paginator(tweets_query, tweets_per_page)

    context = {
        'tweets': tweet_paginator.page(page_num),
        'rank_increment': rank_inc, # Take page number as arg to this fn
        'num_pages': tweet_paginator.num_pages,
        'current_page': page_num,
        'filters': json.dumps(filters),
    }
    return render(request, 'tweets/index.html', context=context)
