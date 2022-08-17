# Generated by Django 4.1 on 2022-08-16 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trending_tweets_app', '0002_mediaattachment_mediatweet_twitterartist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediaattachment',
            name='parent_tweet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trending_tweets_app.mediatweet', to_field='tweet_id'),
        ),
        migrations.AlterField(
            model_name='mediatweet',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trending_tweets_app.twitterartist', to_field='user_id'),
        ),
    ]
