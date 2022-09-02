from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'trending_tweets_app'

urlpatterns = [
    path('', views.tweets, name='trending_tweets'),
]