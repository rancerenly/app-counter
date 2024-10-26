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
