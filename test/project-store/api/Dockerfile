FROM python:3.7

RUN pip install flask

WORKDIR /app

ADD service.py service.py

ENTRYPOINT ["flask", "run"]
