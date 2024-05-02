#!/bin/bash

rm -rf driftnotesapi/migrations
rm db.sqlite3
python3 manage.py makemigrations driftnotesapi
python3 manage.py migrate
python3 manage.py loaddata user
python3 manage.py loaddata category
python3 manage.py loaddata token
python3 manage.py loaddata day
python3 manage.py loaddata event
python3 manage.py loaddata trip
python3 manage.py loaddata usertrip



