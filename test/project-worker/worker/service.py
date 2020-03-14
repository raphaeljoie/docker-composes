import os
from celery import Celery

queue_host = os.getenv('QUEUE_HOST', 'localhost')
queue_port = int(os.getenv('QUEUE_PORT', '5672'))
queue_username = os.getenv('QUEUE_USERNAME', None)
queue_password = os.getenv('QUEUE_PASSWORD', None)

app = Celery('service', broker=f'pyamqp://{queue_username}:{queue_password}@{queue_host}:{queue_port}//')

@app.task
def add(x, y):
    return x + y
