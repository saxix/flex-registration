How to run local development with docker compose
=

Local development can use docker-compose
it will use postgres redis and celery under the hood

Application will be accessible at http://localhost:8000

For the first time you need to run in root project directory
```shell
cp .env.example .env
docker-compose build
docker-compose up
```

each next time

```shell
docker-compose up
```

Other way(stefano)
=

