release: python manage.py migrate
release: python manage.py loaddata data.xml
web: gunicorn d8_hw.wsgi