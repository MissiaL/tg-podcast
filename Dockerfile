FROM python:3.7-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install -r requirements.txt