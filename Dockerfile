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
