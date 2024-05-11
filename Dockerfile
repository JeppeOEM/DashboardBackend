FROM python:3.9-alpine3.13
LABEL maintainer="Team Oxygen"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./sqa-requirements.txt /tmp/sqa-requirements.txt
COPY . /app

WORKDIR /app
EXPOSE 8000

ARG DEV=true
#By using a virtual environment, you ensure that your Python dependencies are isolated
#from the system-level Python installation. This can prevent conflicts with other applications
#or processes running on the same system, we dont have other python instances running so not strictly nececary

#Installing development dependencies that is need to make
# postgres to run, but which are not need in production so are deleted
# again later
####

RUN pip install --upgrade pip
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev
####
RUN pip install -r /tmp/requirements.txt && \
    if [ $DEV = true ]; \
    then pip install -r /tmp/sqa-requirements.txt ; \
    fi
RUN rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user
#give permission to write to the cache which is needed for pip-audit
# RUN chown -R django-user /app
ENV PATH="/py/bin:$PATH"
USER django-user
ENTRYPOINT ["sh", "entrypoint.sh"]