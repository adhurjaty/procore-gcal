FROM python:3.8-slim

LABEL maintainer="adhurjaty@gmail.com"

COPY requirements.txt .
RUN \
    apt-get update -y && \
    apt-get install -y postgresql postgresql-contrib gcc libpq-dev && \
    pip install -r requirements.txt --no-cache-dir
COPY . .
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
