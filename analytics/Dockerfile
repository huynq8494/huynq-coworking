# Use this base image in oder to reduce docker image size and speed up docker build
FROM python:3.10-slim

# Use root user to be able to install apt packages
USER root

# Install apt packages to successfully install postgresql
RUN apt update -y && apt install build-essential libpq-dev -y

# Working directory
WORKDIR /src

# Copy requirements.txt and app from Docker context to the working directory
COPY ./requirements.txt ./*.py .

# Update python modules to successfully build the required modules
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

# Run app when a docker container start
CMD python app.py
