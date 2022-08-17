from django.urls import path
from . import views

app_name = 'trending_tweets_app'

urlpatterns = [
    path('', views.index, name='trending_tweets')
]