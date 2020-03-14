FROM python:3.7

RUN pip install celery

WORKDIR /app

ADD service.py service.py

ENTRYPOINT ["celery", "-A", "service", "worker", "--loglevel=info"]
