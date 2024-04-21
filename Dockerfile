FROM python:3.10-alpine3.19

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip &&  \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/