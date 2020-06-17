FROM python:3.8-slim

LABEL maintainer="adhurjaty@gmail.com"

COPY requirements.txt .
RUN \
    apt-get update -y && \
    apt-get install -y postgresql postgresql-contrib gcc libpq-dev && \
    pip install -r requirements.txt --no-cache-dir 
COPY . .
RUN rm secrets/app.config && \
    mv secrets/app.config.prod secrets/app.config && \
    rm alembic.ini && \
    mv alembic.ini.prod alembic.ini
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
