#!/bin/sh
# set current directory to src
SRC="$(dirname "$0")/../src"
cd $SRC

echo "Current path:"
pwd

WORKERS=2
ADDRESS='0.0.0.0:5000'

gunicorn --workers $WORKERS --bind=$ADDRESS --name=FlourishAPI 'wsgi:create_gunicorn(c="prod")'