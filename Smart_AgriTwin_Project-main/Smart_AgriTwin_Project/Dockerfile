FROM python:3.11-slim
WORKDIR /app
COPY backend/ /app
RUN pip install --no-cache-dir flask flask_sqlalchemy flask_migrate psycopg2-binary flask-jwt-extended werkzeug
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
