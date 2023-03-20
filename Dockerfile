FROM python:3.10

RUN mkdir /searchGPT
RUN mkdir /searchGPT/tmp

WORKDIR /searchGPT

COPY requirements-heroku.txt /searchGPT/tmp/requirements.txt

RUN pip install -r /searchGPT/tmp/requirements.txt

ENV PYTHONPATH /searchGPT/src