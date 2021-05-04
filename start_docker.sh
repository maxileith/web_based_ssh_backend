#!/bin/sh

python manage.py makemigrations &&
python manage.py migrate &&
uwsgi --http "0.0.0.0:80" --module web_based_ssh_backend.wsgi --master --processes 4 --threads 2
