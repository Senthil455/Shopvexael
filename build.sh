#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
cp static/_redirects staticfiles/ || true
python manage.py migrate
