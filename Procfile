web: gunicorn -w 2 -k gthread --threads 4 --timeout 60 --access-logfile - --error-logfile - -b 0.0.0.0:$PORT server:app
