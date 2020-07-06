#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$FLASK_ENV" = "development" -a "$APP" = "web" ]
then
    echo "Creating the database tables..."
    python manage.py create_db

    #Should create a new admin
    python manage.py seed_db
    echo "db seeded"
        echo "Tables created"
fi

exec "$@"