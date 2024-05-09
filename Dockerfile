FROM python:3.9-alpine3.13
LABEL maintainer="Oxygen"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
#WORKDIR instruction sets the working directory for any subsequent RUN,
#CMD, ENTRYPOINT, COPY, and ADD instructions in the Dockerfile.
WORKDIR /app
EXPOSE 8000

ARG DEV=test
RUN python -m venv /py
RUN /py/bin/pip install --upgrade pip
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev
RUN /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi
RUN rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
    --disabled-password \
    --no-create-home \
    django-user
ENV PATH="/py/bin:$PATH"
USER django-user
