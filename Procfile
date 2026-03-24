web: gunicorn Zinocare.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A Zinocare worker --loglevel=info