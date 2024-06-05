
FROM python:3.10.4-slim-bullseye
WORKDIR .

COPY ./requirements.txt ./requirements.txt
COPY ./chatbot ./chatbot
COPY ./startbot.py ./startbot.py
COPY ./messages.json ./messages.json

RUN pip install -r requirements.txt
