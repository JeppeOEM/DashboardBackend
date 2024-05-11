#!/bin/sh

python manage.py check
python manage.py wait_for_db
python manage.py makemigrations
python manage.py migrate
python manage.py save_coins_to_db


case "$RTE" in
    dev )
        echo "** Development mode."
        pip-audit
        isort --skip app/core/migrations .
        echo "***Autopep8 formatting***"
        # corrects linting warnings
        autopep8 --in-place --recursive --exclude app/core/migrations/ .
        echo "***Pylama Linting***"
        pylama -o .pylama.ini .
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m
        python manage.py runserver 0.0.0.0:8000
        ;;
    test )
        echo "** Test mode."
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m --fail-under=70
        pip-audit || exit 1
        ;;
    prod )
        echo "** Production mode."
        pip-audit || exit 1
        python manage.py check --deploy
        ;;
esac
