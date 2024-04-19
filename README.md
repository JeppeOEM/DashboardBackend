app is the name of the service here

docker-compose run --rm app sh -c "python manage.py test"

#create new django project
#docker-compose run --rm app sh -c "django-admin startproject app ."

#lint (start from buttom up, dont affect line number)
# docker-compose run --rm app sh -c "flake8"
# docker-compose run --rm app sh -c "python manage.py test"
#create new PROJECT
# docker-compose run --rm app sh -c "python manage.py startproject NAMEHERE ."

#create new app
# docker-compose run --rm app sh -c "python manage.py startapp NAMEHERE"
when create a new app add it to the main project app settings.py file under INSTALLED_APPS by simply writing the name of folder

# docker-compose build (just building via docker compose)

# psycopg2 IS BEING COMPILED when run with pip based on operating system

## Commands
Management -> commands folder structure to create commands