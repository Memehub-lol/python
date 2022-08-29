#!/bin/bash

if [ "$ENV" == "local" ];
then alembic -c alembic.docker.ini upgrade head;
fi

pip install -e .
mh load stonk-market
gunicorn -c "python:config.gunicorn" "src.flask:APP"