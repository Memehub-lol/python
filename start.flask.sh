#!/bin/bash
alembic -c alembic.docker.ini upgrade head
pip install -e .
mh load stonk-market
mh templates sync
gunicorn -c "python:config.gunicorn" "src.flask:APP"