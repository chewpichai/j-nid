#!/bin/sh
rm database.sqlite
python manage.py syncdb

