#!/bin/sh
set -eu
python qgame/manage.py migrate --noinput
python qgame/manage.py bootstrap_admin
exec gunicorn --chdir qgame qgame.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 1 --threads 2 --timeout 60 --access-logfile - --error-logfile -
