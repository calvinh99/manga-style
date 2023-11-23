from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = 'tweets'

urlpatterns = [
    path('', views.tweets, name='tweets'),
]