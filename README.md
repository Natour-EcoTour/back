pip freeze > requirements.txt
py manage.py makemigrations
py manage.py migrate
py manage.py runserver

python manage.py createsuperuser --username admin --email admin@example.com

pylint --load-plugins=pylint_django natour
