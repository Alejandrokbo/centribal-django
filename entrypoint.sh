#!/bin/sh
sh -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py runserver 8000"
