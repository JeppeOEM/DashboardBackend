FROM python:3.9-alpine3.13
LABEL maintainer="jeppe m. webpage: mrqdt.xyz"
#Print directly to console DONT buffer it
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
#Default dir where commands will be run from when running commands on the docker image
WORKDIR /app
#Expose port to local machine
EXPOSE 8000

ARG DEV=false
#Keeping image lightweight , building with ONE layer
#Using a venv because there might still be some conflicting dependencies with the base image
RUN python -m venv /py && \ 
    /py/bin/pip install --upgrade pip
RUN apk add --update --no-cache postgresql-client
#apk add postgresql-dev \
#virtual dependencies .tmp-build-deps
RUN apk add --update --no-cache --virtual .tmp-build-deps
RUN build-base postgresql-dev musl-dev 
#RUN gcc libc-dev linux-headers postgresql-dev
RUN /py/bin/pip install -r /tmp/requirements.txt
#small if shell script
RUN if [ $DEV = "true" ]; \
    then echo "--DEV BUILD--" && /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi 

#end of shell script
RUN apk del .tmp-build-deps
#requirements is not used after build so it is removed
RUN rm -rf /tmp
# psycopg2 needs some dependencies to build but they are only needed during build
#so virtual dep folder is removed
RUN apk del .tmp-build-deps
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

#Linux path, it defines where executeables can be run    
#Puts /py/bin: infront of the current value of the PATH env
ENV PATH="/py/bin:$PATH"

USER django-user