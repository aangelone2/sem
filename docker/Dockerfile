# syntax=docker/dockerfile:1

# selecting python image
FROM python:3.11-slim

# creating a workdir
WORKDIR /app

# installing system packages, required for psycopg
RUN apt-get update
RUN apt-get -y install gcc postgresql postgresql-contrib libpq-dev

# Copying separately lockfile,
# installation will be performed iif packages change
COPY docker/requirements.txt .

# installing required packages
RUN pip install -r requirements.txt

# copy all other local content host -> container
COPY . .

# launch command
CMD "docker/run.sh"
