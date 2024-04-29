#!/bin/bash

rm -rf driftnotesapi/migrations
rm db.sqlite3
python3 manage.py makemigrations driftnotesapi
python3 manage.py migrate
python3 manage.py loaddata users


