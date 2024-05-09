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
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m
        python manage.py runserver 0.0.0.0:8000
        ;;
    test )
        echo "** Test mode."
        # pip-audit || exit 1
        pip-audit
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m --fail-under=80
        ;;
    prod )
        echo "** Production mode."
        pip-audit || exit 1
        python manage.py check --deploy
        ;;
esac
