web: gunicorn jkr.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2 --log-file - --access-logfile - --error-logfile -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear
