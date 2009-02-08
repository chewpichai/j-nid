#!/bin/sh
rm database.sqlite
python manage.py syncdb
chmod 777 database.sqlite