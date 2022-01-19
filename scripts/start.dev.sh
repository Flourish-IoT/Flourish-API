#!/bin/bash
# set current directory to top level
BASE_DIR="$(dirname "$0")/.."
cd $BASE_DIR
BASE_DIR=$(pwd)

# activate venv
VENV="$BASE_DIR/venv"
source "$VENV/bin/activate"

# set current directory to src
SRC="$BASE_DIR/src"
cd $SRC

echo "Current path:"
pwd

WORKERS=2
ADDRESS='0.0.0.0:5000'
gunicorn --workers $WORKERS --bind=$ADDRESS --name=FlourishAPI 'wsgi:create_gunicorn(c="dev")'