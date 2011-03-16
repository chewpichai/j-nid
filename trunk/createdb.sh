#!/bin/sh
rm database.sqlite
python manage.py syncdb
chmod 775 database.sqlite
