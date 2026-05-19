#!/bin/sh

echo "Waiting for MySQL..."

# Python checking connection MySQL
python -c "
import MySQLdb
import time
import os
while True:
    try:
        MySQLdb.connect(
            host=os.environ.get('DB_HOST', 'db'),
            user=os.environ.get('DB_USER', 'rental_user'),
            password=os.environ.get('DB_PASSWORD', 'rental_password'),
            db=os.environ.get('DB_NAME', 'rental_db')
        )
        print('MySQL started')
        break
    except MySQLdb.OperationalError:
        print('MySQL unavailable - sleeping')
        time.sleep(1)
"
mkdir -p /app/logs

service cron start

python manage.py migrate
python manage.py load_initial_data

# Start the development server
exec "$@"