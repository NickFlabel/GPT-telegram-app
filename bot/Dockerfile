# Pull base image
FROM python:3.10.4-slim-bullseye
# Set work directory
WORKDIR .

# Copy project
COPY ./requirements.txt ./requirements.txt
COPY ./chatbot ./chatbot

# Install dependencies
RUN pip install -r requirements.txt
