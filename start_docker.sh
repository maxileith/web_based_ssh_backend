#!/bin/sh

python manage.py makemigrations &&
python manage.py migrate &&

daphne web_based_ssh_backend.asgi:application -b 0.0.0.0 -p 80
