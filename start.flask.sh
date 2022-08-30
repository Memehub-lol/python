#!/bin/bash

if [ "$ENV" == "local" ]; then
  echo RUNNING ALEMBIC
  alembic -c alembic.docker.ini upgrade head
else
  echo SKIPPING ALEMBIC
fi

pip install -e .
mh load stonk-market
gunicorn -c "python:src.gunicorn" "src.flask:APP"