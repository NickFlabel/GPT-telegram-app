
FROM python:3.10.4-slim-bullseye
WORKDIR .

COPY ./app ./app
COPY ./requirements.txt ./requirements.txt
COPY ./alembic.ini ./alembic.ini
COPY ./migrations ./migrations
COPY ./start.sh ./start.sh

RUN pip install -r requirements.txt