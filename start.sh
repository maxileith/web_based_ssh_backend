#!/bin/sh

while read LINE; do export "$LINE"; done < .env

python manage.py makemigrations &&
python manage.py migrate &&
python manage.py runserver 0.0.0.0:80
