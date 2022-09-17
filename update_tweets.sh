#!/bin/sh
docker run --rm --env-file .env.prod --network mangastyle_backend mangastyle_web:latest python manage.py update_tweets all