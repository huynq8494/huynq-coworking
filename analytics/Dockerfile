FROM python:3.10-slim-buster

USER root

RUN apt update -y && apt install build-essential libpq-dev -y

WORKDIR /src

COPY ./requirements.txt ./*.py .

RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

CMD python app.py
