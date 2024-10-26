# Шаги выполнения задания

## 1. Подготовка структуры проекта
```bash
/counter_app
├── app.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Flask-приложение было немного переделано

```python

import time
import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/counterdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    client_info = db.Column(db.String(256))

# Настройки Redis
cache = redis.Redis(host='redishost', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    user_agent = request.headers.get('User-Agent')

    new_hit = Counter(client_info=user_agent)
    db.session.add(new_hit)
    db.session.commit()

    return 'Hello World! I have been seen {} times.\n'.format(count)

# Создание таблиц в базе данных при старте приложения
with app.app_context():
    db.create_all()

# Запуск приложения
app.run(host='0.0.0.0')
```

## Dockerfile

```Dockerfile
FROM python:3.7-alpine

WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev

COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /code

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

CMD ["flask", "run"]
```

## requirements.txt

```
Flask
Flask-SQLAlchemy
psycopg2-binary
```

## docker-compose.yml

```
version: "3.8"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./app:/code
    environment:
      FLASK_ENV: development
      FLASK_APP: app.py
    depends_on:
      - db
      - redishost
      
  redishost:
    image: "redis:alpine"

  db:
    image: postgres:alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER} #скрыто в .env
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD} #скрыто в .env
      POSTGRES_DB: ${POSTGRES_DB} #скрыто в .env
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  pg_data:
```

## Запуск

```bash
docker-compose up --build
```

## Демонстрация
Переходим на http://localhost:5000
![image](https://github.com/user-attachments/assets/74fbcdde-b606-4d06-9e42-d5f5d838ec19)

