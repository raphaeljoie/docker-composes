# Combine docker-compose files
Takes one or more Docker Compose YAML file and combines them together.
This script handle the conflicts between files and generates a new `docker-composes.yml` file to be later used by `docker-compose`

NB: auxiliary file is required since `docker-compose` cannot work with a STDIN.

## Context
I've been using `docker-compose` intensively for local development. Each of my micro-service contains a docker-compose.

Imagine the following project
```
project-store
- api
    - Dockerfile
    - service.py
- db
    - seed.sql
- docker-compose.yml
```
here the docker-compose used for development will deploy the API, a PostgreSQL db seeded with my `seed.sql` file, and
maybe any GUI to monitor the DB.

Now, I need a worker service
```
project-worker
- worker
    - Dockerfile
    - service.py
- rabbitmq
    - rabbitmq.conf
- docker-compose.yml
```
There, the docker-compose will for sure deploy the worker and a RabbitMQ instance, but also include a mock API to feed 
the queues, and a nice GUI found on Docker hub.

> What if I want now to combine both micro-services?

**The solution**: instead of playing with fancy networking configuration, I decided to create a script to combine both 
`docker-compose.yml` files together
