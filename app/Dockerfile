FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y gcc

WORKDIR /usr/src

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy --ignore-pipfile --dev

CMD python main.py
