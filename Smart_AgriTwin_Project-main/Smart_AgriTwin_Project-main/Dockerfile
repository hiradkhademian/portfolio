FROM python:3.11-slim

WORKDIR /app

COPY backend/ /app

ENV FLASK_APP=app
ENV FLASK_ENV=development
ENV FLASK_RUN_PORT=5000

RUN pip install --no-cache-dir \
    flask \
    flask_sqlalchemy \
    flask_migrate \
    psycopg2-binary \
    flask-jwt-extended \
    werkzeug \
    python-dotenv \
    requests

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
