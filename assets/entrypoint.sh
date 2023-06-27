#!/bin/bash

if [ "$1" == "gunicorn" ]; then
  echo "Running collect static ..."
  python /opt/project/manage.py collectstatic --noinput

  echo "Waiting for db ..."
  until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q'; do
    echo >&2 "Postgres is unavailable - sleeping"
    sleep 1
  done
  echo "Connected to database"

  python3 /opt/project/manage.py migrate --noinput

  if [ $? -ne 0 ]; then
    echo "Migrate failed!" >&2
    exit 1
  fi

  python3 /opt/project/manage.py default_config

  exec  gunicorn --bind 0.0.0.0:8000 --chdir /opt/project --log-level='info' --log-file=- --workers $GUNICORN_WORKER project.wsgi:application

elif [ "$1" == "celery" ]; then
  cd /opt/project
  celery -A settings worker -l INFO

elif [ "$1" == "celery-beat" ]; then
  cd /opt/project
  celery -A settings beat -l INFO

fi
