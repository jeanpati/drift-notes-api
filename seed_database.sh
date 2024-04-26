#!/bin/bash

rm db.sqlite3
rm -rf ./driftnotesapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations driftnotesapi
python3 manage.py migrate driftnotesapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

